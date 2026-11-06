# Hindi Explainer Studio — hosted AI workspace

This is the deployable cloud companion for the existing local-first Hindi Explainer Studio.

## Architecture

- **Hosted web app (Next.js on Vercel):** private browser UI, password gate, OpenAI Responses API backend and web-search-backed research briefs.
- **OpenAI API:** generates ideas, research, scripts, storyboards, revisions and YouTube packaging. The API key is read only by the server.
- **Local computer:** the existing Flask dashboard, project folders, voice recordings, source assets, installed animation engine, FFmpeg and final renders remain on your PC.

The hosted app cannot directly browse your PC's folders, start local processes or access its renderer. It exports a portable JSON handoff which you can keep with the local project. The local dashboard remains available at http://127.0.0.1:5173.

## Deploy on Vercel

1. Import this GitHub repository into Vercel.
2. Set **Root Directory** to **web**.
3. Framework preset: Next.js. Build command: npm run build. Install command: npm install.
4. Add these Production environment variables in Vercel:
   - **OPENAI_API_KEY**: an OpenAI API key with access to the selected model.
   - **OPENAI_MODEL**: optional; defaults to gpt-6-astra.
   - **STUDIO_ACCESS_PASSWORD**: a strong, unique password for this single-owner workspace.
   - **SESSION_SECRET**: a random secret of at least 32 characters. Generate locally with the command below.

    node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

5. Deploy. Keep all secrets out of Git and do not use a NEXT_PUBLIC_ prefix for them.

## Local development

    cd web
    cp .env.example .env.local
    # Fill in OPENAI_API_KEY, STUDIO_ACCESS_PASSWORD and SESSION_SECRET.
    npm install
    npm run dev

Open http://localhost:3000.

## AI tasks

- **Research brief** uses the Responses API web_search tool and requires a search-enabled model.
- Ideas, scripts, storyboards, revisions and YouTube packaging use the Responses API without web search. The visual-code task can generate a standalone HTML/SVG/JavaScript scene that you download, inspect and render locally.
- The selected model is controlled by OPENAI_MODEL.

OpenAI API usage is billed separately from a ChatGPT subscription. Vercel hosting and OpenAI API usage may both incur charges according to their respective plans and usage.

## Security and limitations

- The OpenAI API key stays in server-side environment variables and is never sent to the browser.
- A signed, HTTP-only, seven-day session cookie protects the app. The shared password gate is intended for a personal single-owner deployment, not a public multi-user product.
- This initial web app does not include account registration, cloud project persistence, a database, or a remote-control channel into your PC.
- Do not expose the existing Flask local dashboard directly to the public internet. It is designed to bind to localhost and can execute local commands.
- The browser can export a JSON handoff for research and writing, or a standalone `scene.html` for generated motion graphics. Inspect AI-generated code before running it; copy it into the local project and use your PC for all media production.

## Next integration step

A secure local companion agent can be added later. It should initiate an outbound authenticated connection from your PC to a cloud job queue, rather than opening inbound access to your PC. That agent can then pull approved jobs and run the local renderer against local project files.
