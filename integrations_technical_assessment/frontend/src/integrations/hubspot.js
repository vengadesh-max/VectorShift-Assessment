import { useState, useEffect } from 'react';
import {
    Box,
    Button,
    CircularProgress,
    Typography,
    List,
    ListItem
} from '@mui/material';
import axios from 'axios';

export const HubspotItemsViewer = ({ integrationParams }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleLoadItems = async () => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('credentials', JSON.stringify(integrationParams.credentials));
            const response = await axios.post('http://localhost:8000/integrations/hubspot/get_hubspot_items', formData);
            setItems(response.data);
        } catch (e) {
            const msg =
                e?.response?.data?.detail ||
                e?.response?.data?.message ||
                e?.response?.data ||
                e.message ||
                "Unknown error";
            alert(msg);
        }
        setLoading(false);
    };

    return (
        <Box sx={{ mt: 2 }}>
            <Button
                variant="contained"
                onClick={handleLoadItems}
                disabled={loading || !integrationParams?.credentials}
            >
                {loading ? <CircularProgress size={20} /> : 'Load HubSpot Items'}
            </Button>
            <Box sx={{ mt: 2 }}>
                {items.length > 0 ? (
                    <List>
                        {items.map((item, idx) => (
                            <ListItem key={item.id || idx}>
                                <Typography>
                                    <b>{item.name}</b> (ID: {item.id})<br />
                                    Type: {item.type}<br />
                                    Created: {item.creation_time}<br />
                                    Last Modified: {item.last_modified_time}
                                </Typography>
                            </ListItem>
                        ))}
                    </List>
                ) : (
                    !loading && <Typography>No items loaded yet.</Typography>
                )}
            </Box>
        </Box>
    );
};

export const HubspotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);

    const handleConnectClick = async () => {
        try {
            setIsConnecting(true);
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/authorize`, formData);
            const authURL = response?.data;

            const newWindow = window.open(authURL, 'HubSpot Authorization', 'width=600, height=600');

            const pollTimer = window.setInterval(() => {
                if (newWindow?.closed !== false) { 
                    window.clearInterval(pollTimer);
                    handleWindowClosed();
                }
            }, 200);
        } catch (e) {
            setIsConnecting(false);
            const msg =
                e?.response?.data?.detail ||
                e?.response?.data?.message ||
                e?.response?.data ||
                e.message ||
                "Unknown error";
            alert(msg);
        }
    };

    const handleWindowClosed = async () => {
        try {
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/credentials`, formData);
            const credentials = response.data; 
            if (credentials) {
                setIsConnecting(false);
                setIsConnected(true);
                setIntegrationParams(prev => ({ ...prev, credentials: credentials, type: 'HubSpot' }));
            }
        } catch (e) {
            const msg =
                e?.response?.data?.detail ||
                e?.response?.data?.message ||
                e?.response?.data ||
                e.message ||
                "Unknown error";
            alert(msg);
        } finally {
            setIsConnecting(false);
        }
    };

    useEffect(() => {
        setIsConnected(integrationParams?.credentials ? true : false);
    }, []);

    return (
        <Box sx={{ mt: 2 }}>
            Parameters
            <Box display='flex' alignItems='center' justifyContent='center' sx={{ mt: 2 }}>
                <Button
                    variant='contained'
                    onClick={isConnected ? () => {} : handleConnectClick}
                    color={isConnected ? 'success' : 'primary'}
                    disabled={isConnecting}
                    style={{
                        pointerEvents: isConnected ? 'none' : 'auto',
                        cursor: isConnected ? 'default' : 'pointer',
                        opacity: isConnected ? 1 : undefined
                    }}
                >
                    {isConnected ? 'HubSpot Connected' : isConnecting ? <CircularProgress size={20} /> : 'Connect to HubSpot'}
                </Button>
            </Box>
        </Box>
    );
};
