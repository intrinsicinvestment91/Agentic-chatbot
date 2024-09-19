import * as dotenv from 'dotenv'
dotenv.config()
import * as express from "express"
import { Request, Response } from "express"
import * as session from "express-session";
import * as cors from 'cors'
import helmet from "helmet";
import { ManagementClient, User } from "auth0";
import Stripe from 'stripe';
import { authorize } from './authorize';
import { createProxyMiddleware, Options } from 'http-proxy-middleware';
dotenv.config();


const cookieParser = require('cookie-parser')
const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');
//import bodyParser from 'body-parser'; 

/*
export const managementAPI = new ManagementClient({
    domain: process.env.AUTH0_DOMAIN,
    clientId: process.env.AUTH0_CLIENT_ID,
    clientSecret: process.env.AUTH0_CLIENT_SECRET,
});
*/

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
    apiVersion: '2022-11-15',
    appInfo: {
        name: "gdansk-ai",
        version: "0.0.1",
        url: "https://localhost:3000"
    }
});

const app = express()
app.use(cookieParser());
app.use(cors({
    origin: ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080", "https://localhost:3000/api/buy-tokens", process.env.AUTH0_ISSUER_BASE_URL],
    credentials: true,

}))


app.use(express.json());


app.use(
    session({
        secret: '232', // TODO use not hardcoded secret
        resave: false,
        saveUninitialized: true,
        cookie: {
            maxAge: 24 * 60 * 60 * 1000, // 1 day in milliseconds
            secure: false, // Set to true if using HTTPS
            httpOnly: true, // Prevents client-side JavaScript from accessing the cookie
            sameSite: 'lax' // Controls when cookies are sent
        }
    })
);


const client = jwksClient({
    jwksUri: `https://${process.env.AUTH0_DOMAIN}/.well-known/jwks.json`
});

function getKey(header, callback) {
    client.getSigningKey(header.kid, (err, key) => {
        if (err) {
            callback(err);
        } else {
            const signingKey = key.getPublicKey();
            callback(null, signingKey);
        }
    });
}

function verifyToken(token) {
    return new Promise((resolve, reject) => {
        jwt.verify(token, getKey, {
            audience: process.env.AUTH0_AUDIENCE,//apparnetly its not the url, but its the client ID
            issuer: `https://${process.env.AUTH0_DOMAIN}/`,
            algorithms: ['RS256']
        }, (err, decoded) => {
            if (err) {
                reject(err);
            } else {
                const userId = decoded.sub; // Extract the user ID
                resolve({ userId, decoded });// retyrn data 
            }
        });
    });
}


app.post('/login', async (req, res) => {//"authorize"for Auth0 does not work!
    const { email, name, sub, idToken } = req.body;
    try {
        console.log(idToken)
        if (!idToken) {
            return res.json('no jwt provided')
        }
        // Set a cookie with user data
        // Configure the cookie (e.g., setting httpOnly, secure, maxAge)
        const userId = await verifyToken(idToken);
        console.log('Verified Token:', userId);
        console.log(userId);
        // Respond to the client
        res.status(200).json({ success: true, message: 'authentication correctly set', id: userId });
    }
    catch (error) {
        res.status(400).json(error)
    }
})



// AI-API proxy
app.post('/question', async (req, res, next) => {
    let user: User = undefined;
    const token = req.cookies.jwt
    console.log(token)
    try {
        const auth = await handleUserAuth(token)
        if (auth.error) {
            throw auth.error
        }
        // res.status(200).json('user has been verified')
        const email = auth.success.decoded.email

        const response = await stripe.customers.search({//find email
            query: `email:'${email}'`,
            limit: 1
        });

        if (response.data.length == 0) {
            console.log('No customer found with email:', email);
            res.status(200).json(` no customer found with that email: ${email}` )
        }
        else {
            const customer = response.data[0];
            console.log('Found Customer:', customer.id);

            const subscriptions = await stripe.subscriptions.list({
                customer: customer.id,
                status: 'active',
                limit: 1,
            });

            if (subscriptions.data.length == 0) {
                console.log('No subscription found for the email', email);
                res.status(200).json( ` No subscription  found with that email: ${email}` )
            }
            else{
                const subscriptionItemId = subscriptions.data[0].items.data[0].id;

                const usageRecord = await stripe.subscriptionItems.createUsageRecord(
                   subscriptionItemId,
                    {
                     // The subscription item ID
                    quantity: 1,
                    timestamp: Math.floor(Date.now() / 1000), // Current timestamp
                    action: 'increment',//add one here
                });
                console.log('Usage record added to existing cost:', usageRecord.id);
                next()//goes to the next middleware function(i.e proxy.)
            }
        }

        }
    catch (error) {
            console.log('error found', error)
            //res.clearCookie('jwt');//handle expirations
            res.status(400).json(` error verifying account: ${error}`)
        }

        /* change to data for bitcoin in order to use
        try {
            await managementAPI
                .getUser(
                    {
                        id: req.auth.payload.sub,
                    })
                .then(response => {
                    user = response;
    
                    if (user.user_metadata?.tokens > 0) { // TODO use customizable value here 
                        try {
                            managementAPI
                                .updateUser(
                                    {
                                        id: user.user_id
                                    },
                                    {
                                        user_metadata: {
                                            tokens: Number.parseInt(user?.user_metadata?.tokens) - 1 //TODO it assumes that one token is one response
                                        }
                                    })
                                .then(response => {
                                    console.log("Updated number of tokens", response)
                                })
                                .catch(function (err) {
                                    console.error("Failed to add metadata to user 1 ", err);
                                });
                        } catch (err) {
                            console.error('Failed to add metadata to user 2 ', err)
                        }
                        next();//improtant, this will call the proxy middleware here. 
                    } else {
                        res.status(400).send('No tokens enough');
                        // TODO send voice response
                    }
                })
                .catch(function (err) {
                    console.error("Failed to fetch user data", err);
                });
        } catch (err) {
            console.error('err', err)
        }
            */


    });

const proxyOptions: Options = {
    target: process.env.AI_API_URL,
    changeOrigin: true,
    autoRewrite: true
};

interface AuthSuccess {
    //another object type that we need to specify(like a stripe success object) 
    //in order to access the actual data from the object with the data we actually need       
    decoded: {//we need to specify the type when we get the object, like "userId as AuthSuccess"
        email: string;
    };
    // Other properties
}



interface HandleUserResult {
    //required if we have different return types for the  possibilities of the function ending
    //like an error, or a success
    success?: AuthSuccess; // Optional result message(possibility here for one)
    error?: string;  // Optional error message
}

async function handleUserAuth(token: string): Promise<HandleUserResult> {
    try {
        if (!token) {
            return { error: 'no jwt provided' }
        }
        // Set a cookie with user data
        // Configure the cookie (e.g., setting httpOnly, secure, maxAge)
        const userId = await verifyToken(token);
        // console.log('Verified Token:', userId);
        return { success: userId as AuthSuccess }//to set userId as an object type we need 
    }
    catch (error) {
        return { error: error }
    }
}

//use handleUserAuth for every endpoint that we need authenticated, we can write a bit less code, but we need 
//to manually throw an error from the function due to the  error catch not being caught in the function, or without catch(uncaught exception)
app.get('/verifyUser', async (req, res) => {
    const token = req.cookies.jwt
    try {
        const auth = await handleUserAuth(token)
        if (auth.error) {
            throw auth.error
        }
        res.status(200).json('user has been verified')
    }
    catch (error) {
        console.log('error found ', error)
        //res.clearCookie('jwt');//handle expirations
        res.status(400).json(` error verifying account: ${error}`)
    }
})

// Proxy middleware
app.post('/question', createProxyMiddleware(proxyOptions));//creates  proxy from 8080 to 5600 where AI API is located

app.get('/pregenerated/no_tokens', createProxyMiddleware(proxyOptions));
app.get('/pregenerated/not_logged', createProxyMiddleware(proxyOptions));

// Web API
app.use(express.json({ limit: '5mb' }));
app.use(express.urlencoded({ limit: '5mb' }));

const prefix = '';

export const api = (endpoint: string = '') => `${prefix}${endpoint}`;
const endpointSecret = process.env.WEBHOOK_CODE;

app.post('/webhook', (req, res) => {//wont run if you use 2 different virtual environment.
    const sig = req.headers['stripe-signature'];
    console.log('sig', sig)
    let event;

    try {
        event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
        console.log(event)
    } catch (err) {
        console.log(`⚠️  Webhook signature verification failed.`);
        return res.sendStatus(400);
    }

    // Handle the event
    switch (event.type) {
        case 'checkout.session.completed':
            const session = event.data.object as Stripe.Checkout.Session;
            console.log(`Checkout session completed: ${session.id}`);
            //basically give the user what they want here, and add it here
            //we can add invoicing here.


            break;
        // ... handle other event types if needed
        default:
            console.log(`Unhandled event type ${event.type}`);
        //record the data here with the user email and type using email.
    }

    res.send();
});


app.get("/my-tokens", async (req, res) => {
    let user: User = undefined;
    const token = req.cookies.jwt
    try {
        const auth = await handleUserAuth(token)
        if (auth.error) {
            throw auth.error
        }
        // res.status(200).json('user has been verified')
        const email = auth.success.decoded.email

        const response = await stripe.customers.search({//find email
            query: `email:'${email}'`,
            limit: 1
        });

        if (response.data.length == 0) {
            console.log('No customer found with email:', email);
            res.status(200).json(` no customer found with that email: ${email}` )
        }
        else {
            const customer = response.data[0];
            console.log('Found Customer:', customer.id);

            const subscriptions = await stripe.subscriptions.list({
                customer: customer.id,
                status: 'active',
                limit: 1,
            });
            if (subscriptions.data.length == 0) {
                console.log('No subscription found for the email', email);
                res.status(200).json( ` No subscription  found with that email: ${email}` )
            }
            else{
                const usageRecords = await stripe.subscriptionItems.listUsageRecordSummaries(subscriptions.data[0].items.data[0].id);
                const usageCount = usageRecords.data[0].total_usage; 

                const session = await stripe.billingPortal.sessions.create({
                    customer: customer.id,
                    return_url: 'http://localhost:3000',
                  });
                
                console.log(usageRecords)
                console.log({
                    "id": subscriptions.data[0].id,
                    "status": subscriptions.data[0].status,
                    "start_date": subscriptions.data[0].start_date,
                    "customer": subscriptions.data[0].customer,
                    "quantity": usageCount, 
                    "portal_url": session.url
                    })
                res.status(200).json( {
                    "id": subscriptions.data[0].id,
                    "status": subscriptions.data[0].status,
                    "start_date": subscriptions.data[0].start_date,
                    "customer": subscriptions.data[0].customer,
                    "quantity": usageCount, 
                    "portal_url": session.url
                    }
                )
        }
    }
    }
    catch(error){   
        res.status(400).json(` error fetching data: ${error}`)
    }
    /*
    try {
        const userId = req.auth.payload.sub; // Ensure `req.user.sub` contains a valid Auth0 user ID
        console.log("userId", userId)

        await managementAPI
            .getUser(
                {
                    id: req.auth.payload.sub,
                })
            .then(response => {
                user = response;
                res.status(200).json({ 'tokens': user.user_metadata.tokens });
            })
            .catch(function (err) {
                console.error("Failed to fetch user data", err);
            });
    } catch (err) {
        console.error('err', err)
    }
        */

});


app.post('/buy-tokens', async (req, res) => {
    // let user: User = undefined;
    /*
    try {
        await managementAPI
            .getUser(
                {
                    id: req.auth.payload.sub,
                })
            .then(response => {
                user = response;
            })
            .catch(function (err) {
                console.error("Failed to fetch user data", err);
            });
    } catch (err) {
        console.error('err', err)
    }
        */
    
    const token = req.cookies.jwt
    console.log(token)
    try {
        const auth = await handleUserAuth(token)
        console.log(auth.success.decoded.email)
        const session = await stripe.checkout.sessions.create({
            billing_address_collection: 'auto',
            line_items: [
                {
                    price: process.env.PRICE_ID,

                },
            ],
            customer_email: auth.success.decoded.email,
            mode: 'subscription',
            success_url: process.env.CLIENT_URL,
            cancel_url: process.env.CLIENT_URL,
        });
        res.status(200).json({ 'redirectUrl': session.url });
    }
    catch (error) {
        res.status(400).json(`error verifying account: ${error}`)
    }

});


app.use(function (req, res, next) {
    console.log("Request to path that doesn't exist")
    const err = new Error('Not Found') as any;
    err.status = 404;
    next(err);
});

// Error handlers
app.use(function (err, req: Request, res: Response,) {
    console.log('Unexpected error', err)
    //res.status(err.status || 400).json({ "Error: ": "An error occured" })
});

process.on('uncaughtException', function (err) {
    console.log('uncaughtException', err);
});

console.log('Server started')
app.listen(8000, () => {
    console.log('listening on 8000')
})