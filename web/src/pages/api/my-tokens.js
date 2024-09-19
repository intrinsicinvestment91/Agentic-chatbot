import { getAccessToken } from '@auth0/nextjs-auth0';
import axios from 'axios';
import { api } from 'utils/api';
const getAuth0Token = async () => {
    const url = 'https://dev-vfn5hppuhadr3tvy.us.auth0.com/oauth/token';
    const data = {
        client_id: 'c15XpFXoGRJcwBRjHnx8m7RjnoFAMrNC',
        client_secret: 'mz2SLgyeRVGU45kHOh5zhS741C9-Tuf3A0hMCt6VtvyYmfZyPumGNi31cxNi3fEz',
        audience: 'https://dev-vfn5hppuhadr3tvy.us.auth0.com/api/v2/',
        grant_type: 'client_credentials'
    };

    try {
        const response = await axios.post(url, data, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        return response.data.access_token;
    } catch (error) {
        console.error('Error fetching token:', error.response ? error.response.data : error.message);
        throw error;
    }
};
export default (async (req, res) => {
    try {
        /*
        const { accessToken } = await getAccessToken(req, res, {
            scopes: ['openid profile email']
        });
        */

        const accessToken = await getAuth0Token()
        const response = await axios.get(api('my-tokens'),
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`
                },
            }).then((res) => {
                return res
            }).catch((err) => {
                console.log(err);
                return err
            });

        res.status(response.status || 200).send(response.data)
    } catch (errorWrapped) {
        const error = errorWrapped;
        console.error(error);
        console.log("error here")
        res.status(error.status || 400).json({
            code: error.code,
            error: error.message
        });
    }
});
