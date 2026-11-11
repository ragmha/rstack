#!/usr/bin/env node
// Serves skills/ over stdio with the MCP Skills extension (io.modelcontextprotocol/skills).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { McpServer } from '@modelcontextprotocol/server';
import { loadSkills } from '@modelcontextprotocol/server/ext/skills/node';
import { serveStdio } from '@modelcontextprotocol/server/stdio';

const { version } = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8'));
const skills = await loadSkills(fileURLToPath(new URL('../skills', import.meta.url)));

serveStdio(() => {
  const server = new McpServer({ name: 'rstack', version });
  skills.attach(server);
  return server;
});
