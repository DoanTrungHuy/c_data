/** @type {import('next').NextConfig} */
const isGithubPages = process.env.GITHUB_PAGES === 'true';

const nextConfig = {
  reactStrictMode: true,
  // Khi build deploy lên GitHub Pages thì kích hoạt static export
  ...(isGithubPages
    ? {
        output: 'export',
        basePath: '/c_data',
        assetPrefix: '/c_data/',
        trailingSlash: true,
      }
    : {
        async rewrites() {
          const backendUrl =
            process.env.API_URL ||
            process.env.NEXT_PUBLIC_API_URL ||
            'http://localhost:8000';

          return [
            {
              source: '/api/v1/:path*',
              destination: `${backendUrl}/api/v1/:path*`,
            },
          ];
        },
      }),
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
  },
};

module.exports = nextConfig;
