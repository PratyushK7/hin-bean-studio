#!/usr/bin/env node
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile, mkdir, stat } from "node:fs/promises";
import { spawn, execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { once } from "node:events";

const RENDER_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = path.resolve(RENDER_DIR, "..");
const INDEX_FILE = path.join(RENDER_DIR, "index.html");
const SCENE_FILE = path.join(RENDER_DIR, "scene.js");
const SCRIPT_FILE = path.join(PROJECT_DIR, "script.json");
const STORYBOARD_FILE = path.join(PROJECT_DIR, "storyboard.json");

function argsOf(argv) {
  const out = { fps: 24, quality: 92, stills: false, times: null, audio: null, output: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--stills") out.stills = true;
    else if (a === "--audio") out.audio = argv[++i];
    else if (a === "--out") out.output = argv[++i];
    else if (a === "--fps") out.fps = Number(argv[++i]);
    else if (a === "--quality") out.quality = Number(argv[++i]);
    else if (a === "--times") out.times = String(argv[++i] || "").split(",").map(Number).filter(Number.isFinite);
    else if (a === "--help" || a === "-h") out.help = true;
    else throw new Error("Unknown argument: " + a);
  }
  return out;
}

function usage() {
  console.log([
    "UPI local Canvas renderer",
    "",
    "Preview the 16 scenes without voice:",
    "  npm run preview -- --out ./stills",
    "",
    "Render with your own recorded narration:",
    "  npm run render -- --audio ../audio/hindi-voice.wav --out ../upi-behind-the-scan.mp4",
    "",
    "Options: --fps 24 --quality 92 --stills --times 0,1,2",
    "Final video requires an audio WAV/MP3 and ffmpeg + ffprobe on PATH."
  ].join("\n"));
}

function resolveRenderPath(value) {
  if (!value) return null;
  return path.isAbsolute(value) ? value : path.resolve(RENDER_DIR, value);
}

function commandOutput(command, argv) {
  try {
    return execFileSync(command, argv, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  } catch (error) {
    const detail = error?.stderr?.toString?.() || error?.message || String(error);
    throw new Error(command + " failed: " + detail);
  }
}

function audioDuration(file) {
  const raw = commandOutput("ffprobe", [
    "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", file
  ]);
  const seconds = Number(raw);
  if (!Number.isFinite(seconds) || seconds <= 0) throw new Error("Could not read a positive audio duration from " + file);
  return seconds;
}

async function loadPlan() {
  const [scriptRaw, boardRaw] = await Promise.all([
    readFile(SCRIPT_FILE, "utf8"), readFile(STORYBOARD_FILE, "utf8")
  ]);
  const script = JSON.parse(scriptRaw);
  const storyboard = JSON.parse(boardRaw);
  if (!Array.isArray(script) || !script.length) throw new Error("script.json must be a non-empty array of spoken sentences.");
  if (!Array.isArray(storyboard) || storyboard.length !== 16) throw new Error("Expected 16 storyboard scenes; found " + (storyboard?.length ?? "invalid"));
  const covered = new Set();
  const scenes = storyboard.map((scene, index) => {
    const [first, last] = scene.script_lines || [];
    if (!Number.isInteger(first) || !Number.isInteger(last) || first < 0 || last >= script.length || first > last) {
      throw new Error("Invalid script_lines range in storyboard scene " + scene.id);
    }
    let words = 0;
    for (let line = first; line <= last; line++) {
      words += String(script[line]).trim().split(/\s+/).filter(Boolean).length;
      covered.add(line);
    }
    return { ...scene, index, words: Math.max(1, words) };
  });
  const missing = script.map((_,i)=>i).filter(i=>!covered.has(i));
  if (missing.length) throw new Error("Storyboard does not cover script sentence indices: " + missing.join(", "));
  return { script, scenes, totalWords: scenes.reduce((sum,s)=>sum+s.words,0) };
}

function timelineFor(scenes, totalSeconds) {
  let cursor = 0;
  const totalWords = scenes.reduce((sum,s)=>sum+s.words,0);
  return scenes.map((scene, index) => {
    const duration = index === scenes.length - 1
      ? totalSeconds - cursor
      : totalSeconds * scene.words / totalWords;
    const row = { ...scene, start: cursor, end: cursor + duration, duration };
    cursor += duration;
    return row;
  });
}

async function startPreviewServer() {
  const html = await readFile(INDEX_FILE);
  const js = await readFile(SCENE_FILE);
  const server = createServer((request, response) => {
    const pathname = new URL(request.url || "/", "http://127.0.0.1").pathname;
    if (pathname === "/" || pathname === "/index.html") {
      response.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
      response.end(html);
    } else if (pathname === "/scene.js") {
      response.writeHead(200, { "content-type": "text/javascript; charset=utf-8", "cache-control": "no-store" });
      response.end(js);
    } else {
      response.writeHead(404); response.end("Not found");
    }
  });
  await new Promise((resolve,reject)=>{server.once("error",reject);server.listen(0,"127.0.0.1",resolve);});
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("Could not bind local preview server.");
  return { server, url: "http://127.0.0.1:" + address.port + "/" };
}

async function openPage() {
  const { server, url } = await startPreviewServer();
  try {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 1
    });
    page.on("pageerror", error => console.error("[browser]", error.message));
    await page.goto(url, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    const ready = await page.evaluate(() => typeof window.renderFrame === "function");
    if (!ready) throw new Error("scene.js did not expose window.renderFrame().");
    return { browser, page, server };
  } catch (error) {
    server.close();
    throw error;
  }
}

async function renderStills(options, plan) {
  const outputDir = resolveRenderPath(options.output || "stills");
  await mkdir(outputDir, { recursive: true });
  const { browser, page, server } = await openPage();
  try {
    const times = options.times?.length ? options.times : plan.scenes.map((_,i)=>i);
    for (let i=0;i<times.length;i++) {
      const sceneIndex = options.times?.length ? Math.max(0,Math.min(15,Math.floor(times[i]))) : i;
      await page.evaluate(({sceneIndex,progress})=>window.renderFrame(sceneIndex,progress),{sceneIndex,progress:0.62});
      const file = path.join(outputDir,"scene-"+String(sceneIndex+1).padStart(2,"0")+".png");
      await page.screenshot({ path:file, type:"png" });
      console.log("Saved " + file);
    }
    console.log("Preview complete: " + outputDir);
  } finally {
    await browser.close();
    server.close();
  }
}

async function renderVideo(options, plan) {
  if (!options.audio) throw new Error("Final rendering requires --audio ../audio/hindi-voice.wav. Record your narration first.");
  const audio = resolveRenderPath(options.audio);
  try { await stat(audio); } catch { throw new Error("Voice recording not found: " + audio); }
  const duration = audioDuration(audio);
  const fps = Math.round(options.fps);
  if (!Number.isFinite(fps) || fps < 12 || fps > 60) throw new Error("--fps must be between 12 and 60.");
  if (!Number.isFinite(options.quality) || options.quality < 60 || options.quality > 100) throw new Error("--quality must be between 60 and 100.");
  const output = options.output ? resolveRenderPath(options.output) : path.join(PROJECT_DIR,path.basename(PROJECT_DIR)+".mp4");
  await mkdir(path.dirname(output), { recursive:true });
  const timeline = timelineFor(plan.scenes,duration);
  const fpsCount = Math.ceil(duration*fps);
  const ffmpegArgs = [
    "-y","-hide_banner","-loglevel","warning",
    "-f","image2pipe","-vcodec","mjpeg","-r",String(fps),"-i","pipe:0",
    "-i",audio,
    "-map","0:v:0","-map","1:a:0",
    "-frames:v",String(fpsCount),"-shortest",
    "-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","192k","-movflags","+faststart",output
  ];
  console.log("Voice duration : " + duration.toFixed(2) + " seconds");
  console.log("Video timeline : 16 scenes, weighted by script sentence word counts");
  console.log("Frame rate     : " + fps + " fps");
  console.log("Output         : " + output);
  const ffmpeg = spawn("ffmpeg",ffmpegArgs,{stdio:["pipe","ignore","pipe"]});
  let stderr="";
  ffmpeg.stderr.on("data",chunk=>{stderr=(stderr+chunk.toString()).slice(-12000);});
  const ffmpegExit = new Promise((resolve,reject)=>{
    ffmpeg.once("error",reject);
    ffmpeg.once("close",(code)=>code===0?resolve():reject(new Error("ffmpeg exited with code "+code+"\n"+stderr)));
  });
  const { browser, page, server } = await openPage();
  try {
    let sceneCursor=0;
    for(let frame=0;frame<fpsCount;frame++){
      const time=Math.min(duration-0.0001,frame/fps);
      while(sceneCursor<timeline.length-1 && time>=timeline[sceneCursor].end)sceneCursor++;
      const scene=timeline[sceneCursor];
      const progress=Math.max(0,Math.min(1,(time-scene.start)/scene.duration));
      await page.evaluate(({index,progress})=>window.renderFrame(index,progress),{index:scene.index,progress});
      const jpeg=await page.screenshot({type:"jpeg",quality:options.quality});
      if(!ffmpeg.stdin.write(jpeg))await once(ffmpeg.stdin,"drain");
      if(frame%Math.max(1,fps*10)===0){
        process.stdout.write("\rRendering "+(100*frame/fpsCount).toFixed(1)+"%  ("+frame+"/"+fpsCount+" frames)");
      }
    }
    ffmpeg.stdin.end();
    await ffmpegExit;
    console.log("\nRendered successfully: "+output);
    console.log("Note: shot boundaries are estimated from script word counts, not speech alignment. Review the edit against your actual narration.");
  } catch(error) {
    ffmpeg.kill("SIGTERM");
    throw error;
  } finally {
    await browser.close();
    server.close();
  }
}

async function main(){
  const options=argsOf(process.argv.slice(2));
  if(options.help){usage();return;}
  const plan=await loadPlan();
  if(options.stills){await renderStills(options,plan);return;}
  await renderVideo(options,plan);
}

main().catch(error=>{
  console.error("\nRender failed: "+(error?.message||error));
  console.error("\nRun node render.mjs --help for usage.");
  process.exitCode=1;
});
