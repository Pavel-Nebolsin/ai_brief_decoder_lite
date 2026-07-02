import { defineConfig } from 'wxt';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  modules: ['@wxt-dev/module-react'],
  vite: () => ({
    plugins: [tailwindcss()],
  }),
  manifest: {
    name: 'AI Brief Decoder Lite',
    description: 'Decode client briefs into structured summaries',
    host_permissions: ['http://localhost:8000/*'],
  },
});
