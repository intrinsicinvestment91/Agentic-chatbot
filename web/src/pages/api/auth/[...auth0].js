import { handleAuth, handleLogin, handleCallback, handleLogout } from '@auth0/nextjs-auth0';
import axios from 'axios'
export default handleAuth({
    login: handleLogin({
        authorizationParams: {
            audience: process.env.AUTH0_AUDIENCE, // Your API audience
            scope: 'openid profile email offline_access', // Scopes required
        }
    }),
    callback: handleCallback({
        afterCallback: async (req, res, session, state) => {
            // Send data to your backend after authentication
                
            // Set the session ID as a cookie with default settings
             // Cookie expires in 7 days
                // Extract user information from session
                try {
                    // Extract user information from session
                    const idToken = session?.idToken; // This should be available after login
                    console.log(idToken)
                    // Example: Send ID Token and other user data to your backend
                    const userData = {
                        email: session.user.email,
                        name: session.user.name,
                        sub: session.user.sub,
                        idToken: idToken // Include ID Token if needed
                    };
                    //set cookie here
                    const cookie = `jwt=${idToken}; Path=/; HttpOnly; SameSite=Lax; Max-Age=3600`;
                    res.setHeader('Set-Cookie', cookie);
                    console.log(cookie)
                    // Send user data to backend
                    const response = await axios.post(`http://localhost:8000/login`, userData, { 
                        credentials: 'include',
                        withCredentials: true, 
                        
                    });
                    console.log('Backend result:', response.data);
    
                    // Continue with the session
                    return session;
                } catch (error) {
                    console.error('Error sending data to backend:', error);
                    return session;
                }
        
    }}),
    
})