import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import MuiCard from '@mui/material/Card';
import Checkbox from '@mui/material/Checkbox';
import FormLabel from '@mui/material/FormLabel';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import { Alert } from '@mui/material';
import Link from '@mui/material/Link';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import { useNavigate, Link as RouterLink } from 'react-router-dom'; // Import RouterLink
import CircularProgress from '@mui/material/CircularProgress';

const Card = styled(MuiCard)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignSelf: 'center',
  width: '100%',
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  boxShadow:
    'hsla(220, 30%, 5%, 0.05) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.05) 0px 15px 35px -5px',
  [theme.breakpoints.up('sm')]: {
    width: '100%',
    maxWidth: '450px', // keeps it from getting too wide on large screens
    padding: theme.spacing(4),
  },
  [theme.breakpoints.down('sm')]: {
    width: '100%',
    padding: theme.spacing(2), // smaller padding on mobile
},

}));

export default function SignInCard() {
  const [emailError, setEmailError] = React.useState(false);
  const [emailErrorMessage, setEmailErrorMessage] = React.useState('');
  const [passwordError, setPasswordError] = React.useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [alert,setAlert] = React.useState(null);
  const navigate = useNavigate();

  const handleSubmit = async() => {

    if (validateInputs()) {
      console.log(document.getElementById('email').value);
      console.log(document.getElementById('password').value);
      const url  = "http://localhost:5000/login-verify";
      
      try{
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
          }),
        });
        const data = await response.json();
        if (response.ok) {
          if(data.success == true){
            sessionStorage.setItem("email",document.getElementById('email').value);
            setAlert({"type":"success","message":"Login Successful"});
            sessionStorage.setItem('navigateToUI','true')
            navigate('/UI');
          }
          else{
            setAlert({"type":"error","message":"Login Failed : Invalid Credentials"});
          }
        } else {
          console.log(data);
          setAlert({"type":"error","message":"Server Error : Please contact the administrator"});
        }
      }catch (error) {
        setAlert({"type":"error","message":"Server Error : Please contact the administrator"});
      }
    }}

  const validateInputs = () => {
    const email = document.getElementById('email');
    const password = document.getElementById('password');

    let isValid = true;

    if (!email.value || !/\S+@\S+\.\S+/.test(email.value)) {
      setEmailError(true);
      setEmailErrorMessage('Please enter a valid email address.');
      isValid = false;
    } else {
      setEmailError(false);
      setEmailErrorMessage('');
    }

    if (!password.value || password.value.length < 6) {
      setPasswordError(true);
      setPasswordErrorMessage('Password must be at least 6 characters long.');
      isValid = false;
    } else {
      setPasswordError(false);
      setPasswordErrorMessage('');
    }

    return isValid;
  };

  return (
    <Card variant="outlined">
      <Box sx={{ display: { xs: 'flex', md: '8' } }}></Box>
      <Typography
        component="h1"
        variant="h4"
        sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.30rem)' }}
      >
        UKCP Chatbot Sign in
      </Typography>
      <Box
        component="form"
        onSubmit={handleSubmit}
        noValidate
        autoComplete="off"
        sx={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 2 }}
      >
        <FormControl>
          <FormLabel htmlFor="email">Email</FormLabel>
          <TextField
            error={emailError}
            helperText={emailErrorMessage}
            id="email"
            type="email"
            name="email"
            placeholder="your@email.com"
            autoFocus
            required
            autoComplete="off"
            fullWidth
            variant="outlined"
            color={emailError ? 'error' : 'primary'}
          />
        </FormControl>
        <FormControl>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <FormLabel htmlFor="password">Password</FormLabel>
          </Box>
          <TextField
            error={passwordError}
            helperText={passwordErrorMessage}
            name="password"
            placeholder="••••••"
            type="password"
            id="password"
            autoFocus
            required
            autoComplete="off"
            fullWidth
            variant="outlined"
            color={passwordError ? 'error' : 'primary'}
          />
        </FormControl>
        <FormControlLabel
          control={<Checkbox value="remember" color="primary" />}
          label="Remember me"
        />
        <Button
          type="button"
          fullWidth
          variant="contained"
          onClick={handleSubmit}
          disabled={loading} // Disable button during loading
          startIcon={loading && <CircularProgress size={20} />} // Add spinner to button
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </Button>
        <Typography sx={{ textAlign: 'center' }}>
          Don&apos;t have an account?{' '}
          <RouterLink to="/signup" style={{ textDecoration: 'none' }}>
            <Link variant="body2" sx={{ alignSelf: 'center' }}>
              Sign up
            </Link>
          </RouterLink>
        </Typography>
        <Typography fontSize={'10px'} sx={{ textAlign: 'center' }}>
          The content produced by the chatbot is AI-generated and may not always be accurate. Whilst we strive for accuracy, we encourage users to verify important information. The Met Office does not endorse the chatbot’s output. Met Office intellectual property is protected by Crown copyright <Link variant="body2" 
          href = "https://eur03.safelinks.protection.outlook.com/?url=https%3A%2F%2Fwww.nationalarchives.gov.uk%2Fdoc%2Fopen-government-licence%2Fversion%2F3%2F&data=05%7C02%7Cab1574%40exeter.ac.uk%7Ca9348b6628b74365e38c08ddb232d74f%7C912a5d77fb984eeeaf321334d8f04a53%7C0%7C0%7C638862653628897149%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=QHfi4076phprowYr3GBT4gGmPbywCC4wNgg2gfMNdQU%3D&reserved=0" 
          sx={{ alignSelf: 'center' }}> (OGL) </Link>.
          The UKCP18 chatbot is part of a research study. This study collects chatbot interaction to better understand user experiences, with access restricted to Arjun Biswas (a.biswas@exeter.ac.uk) and a collaborator from the University of Bath (Dr. Sachini Weerawardhana). 
          Identifiable data is securely stored on encrypted platform (Digital Ocean) and will be anonymised 10 days after submitting the follow-up survey, 
          after which individual data cannot be withdrawn. Anonymised data may be shared with the wider research team, and all data will be permanently deleted on 28 Feb 2035. 
          Participants can withdraw consent at any time before anonymisation, and all data handling complies with UK General Data Protection Regulation (GDPR).
        </Typography>
      </Box>
      {alert && <Alert severity={alert.type}>{alert.message}</Alert>}
    </Card>
  );
}