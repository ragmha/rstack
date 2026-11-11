#!/usr/bin/env node
// Serves skills/ over stdio: the MCP Skills extension (io.modelcontextprotocol/skills) for hosts
// that support it, plus one prompt per skill for hosts that do not yet.
import { readFileSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { McpServer } from '@modelcontextprotocol/server';
import { loadSkills } from '@modelcontextprotocol/server/ext/skills/node';
import { serveStdio } from '@modelcontextprotocol/server/stdio';

const root = fileURLToPath(new URL('../skills', import.meta.url));
const { version } = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8'));
const skills = await loadSkills(root);

serveStdio(() => {
  const server = new McpServer({ name: 'rstack', version });
  skills.attach(server);
  for (const { frontmatter: { name, description } } of skills.entries) {
    const dir = join(root, name);
    server.registerPrompt(name, { description }, async () => ({
      messages: [{
        role: 'user',
        content: {
          type: 'text',
          text: `${await readFile(join(dir, 'SKILL.md'), 'utf8')}\n\nResolve relative paths in this skill against ${dir}.`,
        },
      }],
    }));
  }
  return server;
});
