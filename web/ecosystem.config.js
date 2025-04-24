module.exports = {
  apps: [
    {
      name: 'web',
      script: 'npm run start',
      args: '--prod',
      cwd: 'H:\\fd_project\\FD\\FD_Reid_Web\\web',
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
      },
    },
  ],
};