import httpProxyMiddleware from "next-http-proxy-middleware";
import { getAccessToken } from '@auth0/nextjs-auth0';

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
/*
export const config = {
    api: {
        bodyParser: false,
    },
}
*/
export default async function handler(req, res) {
   /* const { accessToken } = await getAccessToken(req, res, {
        scopes: ['openid','profile']
    });
    console.log(accessToken)
    */
    httpProxyMiddleware(req, res, {
        target: `${process.env.CHATBOT_API_URL}question`,
        ignorePath: true,
        headers: {
            //Authorization: `Bearer ${accessToken}`,
            "chatbot-api-key": process.env.CHATBOT_API_KEY
        },
        onProxyRes: (proxyRes, req, res) => {
            // Add CORS headers to the response
            proxyRes.headers['Access-Control-Allow-Origin'] = '*'; // Adjust this according to your security needs
            proxyRes.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
            proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, chatbot-api-key';
        },
        onError: (err, req, res) => {
            console.error('Error proxying the request:', err);
            res.status(500).json({ message: 'Error proxying the request' });
        },
    });
}
