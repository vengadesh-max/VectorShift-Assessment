import { useState, useEffect } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
    Typography
} from '@mui/material';
import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { HubspotIntegration, HubspotItemsViewer } from './integrations/hubspot';
import { DataForm } from './data-form';

const integrationMapping = {
    'Notion': NotionIntegration,
    'Airtable': AirtableIntegration,
    'HubSpot': HubspotIntegration,
};

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);

    const CurrIntegration = currType ? integrationMapping[currType] : null;

    useEffect(() => {
        setIntegrationParams({});
    }, [currType]);

    return (
        <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' sx={{ width: '100%', p: 2 }}>
            <Typography variant="h4" component="h1" gutterBottom>Integration Form</Typography>
            <Box display='flex' flexDirection='column' sx={{ width: 300 }}>
                <TextField
                    label="User"
                    value={user}
                    onChange={(e) => setUser(e.target.value)}
                    sx={{ mt: 2 }}
                    fullWidth
                />
                <TextField
                    label="Organization"
                    value={org}
                    onChange={(e) => setOrg(e.target.value)}
                    sx={{ mt: 2 }}
                    fullWidth
                />
                <Autocomplete
                    id="integration-type-select"
                    options={Object.keys(integrationMapping)}
                    sx={{ width: '100%', mt: 2 }}
                    renderInput={(params) => <TextField {...params} label="Integration Type" />}
                    onChange={(e, value) => setCurrType(value)}
                    value={currType}
                />
            </Box>

            {currType && (
                <Box sx={{ mt: 4, width: '100%', maxWidth: 400 }}>
                    <Typography variant="h5" gutterBottom>{currType} Integration</Typography>
                    <CurrIntegration
                        key={currType}
                        user={user}
                        org={org}
                        integrationParams={integrationParams}
                        setIntegrationParams={setIntegrationParams}
                    />
                </Box>
            )}

            {integrationParams?.credentials && (
                <Box sx={{ mt: 4, width: '100%', maxWidth: 400 }}>
                    <Typography variant="h5" gutterBottom>Loaded Data</Typography>
                    {currType === "HubSpot" ? (
                        <HubspotItemsViewer integrationParams={integrationParams} />
                    ) : (
                        <DataForm integrationType={integrationParams?.type} credentials={integrationParams?.credentials} />
                    )}
                </Box>
            )}
        </Box>
    );
};
