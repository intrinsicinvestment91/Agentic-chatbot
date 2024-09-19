import { withApiAuthRequired, getAccessToken } from '@auth0/nextjs-auth0';
import axios from 'axios';
import { api } from 'utils/api';

export default (async (req, res) => {
    try {
        
        /*const { accessToken } = await getAccessToken(req, res, {
            scopes: ['openid profile email']
        });
        */

        const response = await axios.post('http://localhost:8000/buy-tokens', {},
            {
               /* headers: {
                    Authorization: `Bearer ${accessToken}`
                },
                */
               
                headers: { 'Content-Type': 'application/json' },
                withCredentials: true, 
                
            }).then((res) => {
                return res
            }).catch((err) => {
                console.log(err);
                return err
            });

        res.status(response.status || 200).json(response.data);
    } catch (errorWrapped) {
        const error = errorWrapped;
        console.error(error);
        res.status(error.status || 400).json({
            code: error.code,
            error: error.message
        });
    }
});
