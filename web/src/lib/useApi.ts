import * as React from 'react';
import axios, { AxiosRequestConfig } from 'axios';

// Initial state setup
export function initialState(args: { error?: any; isLoading?: boolean; response?: any }): any {
    return {
        response: null,
        error: null,
        isLoading: true,
        ...args
    };
}

// Custom hook for POST requests
export const usePost = (
    url: string,
    data: any = {},
    config: AxiosRequestConfig<any> = {},
): {
    error: unknown;
    isLoading: boolean;
    response: any;
} => {
    const [state, setState] = React.useState(() => initialState({}));

    React.useEffect(() => {
        // Check if running on the client side
        if (typeof window === 'undefined') return;

        const fetchData = async () => {
            try {
                const res = await axios.post(url, data, config);
                setState(
                    res.status >= 400
                        ? initialState({ error: await res.data, isLoading: false })
                        : initialState({ response: await res.data, isLoading: false })
                );
            } catch (error) {
                setState(
                    initialState({
                        error: { error: (error as any).message },
                        isLoading: false
                    })
                );
            }
        };

        fetchData();
    }, [url, data, config]);

    return state;
};

// Custom hook for GET requests
export const useGet = (
    url: string,
    config: AxiosRequestConfig<any> = {},
): {
    error: unknown;
    isLoading: boolean;
    response: any;
} => {
    const [state, setState] = React.useState(() => initialState({}));

    React.useEffect(() => {
        // Check if running on the client side
        if (typeof window === 'undefined') return;

        const fetchData = async () => {
            try {
                const res = await axios.get(url, config);
                setState(
                    res.status >= 400
                        ? initialState({ error: res.data, isLoading: false })
                        : initialState({ response: res.data, isLoading: false })
                );
            } catch (error) {
                setState(
                    initialState({
                        error: { error: (error as any).message },
                        isLoading: false
                    })
                );
            }
        };

        fetchData();
    }, [url, config]);

    return state;
};

// Custom hook for generic API requests
const useApi = (
    url: RequestInfo,
    options: RequestInit = {},
    body: any = {}
): {
    error: unknown;
    isLoading: boolean;
    response: any;
} => {
    const [state, setState] = React.useState(() => initialState({}));

    React.useEffect(() => {
        // Check if running on the client side
        if (typeof window === 'undefined') return;

        const fetchData = async () => {
            try {
                const res = await fetch(url, {
                    ...options,
                    body: JSON.stringify(body)
                });

                if (res.status >= 400) {
                    setState(
                        initialState({
                            error: await res.json(),
                            isLoading: false
                        })
                    );
                } else {
                    setState(
                        initialState({
                            response: await res.json(),
                            isLoading: false
                        })
                    );
                }
            } catch (error) {
                setState(
                    initialState({
                        error: { error: (error as any).message },
                        isLoading: false
                    })
                );
            }
        };

        fetchData();
    }, [url, options, body]);

    return state;
};

export default useApi;