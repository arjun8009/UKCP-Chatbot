import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import MuiCard from '@mui/material/Card';
import Checkbox from '@mui/material/Checkbox';
import FormLabel from '@mui/material/FormLabel';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Link from '@mui/material/Link';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
//import ForgotPassword from './ForgotPassword';
import { useNavigate } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import { Alert } from '@mui/material';

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
    width: '450px',
  },

 
}));

export default function SignUpCard() {
  const [emailError, setEmailError] = React.useState(false);
  const [emailErrorMessage, setEmailErrorMessage] = React.useState('');
  const [passwordError, setPasswordError] = React.useState(false);
  const [passwordErrorMessage, setPasswordErrorMessage] = React.useState('');
  const [open, setOpen] = React.useState(false);
  const navigate = useNavigate();
  const [loading, setLoading] = React.useState(false);
  const[alert,setAlert] = React.useState(null);

  const handleClickOpen = () => {
    setOpen(true);
  };


  const handleSubmit = async() => {
    // Validate the inputs before navigation
    console.log(document.getElementById('email').value)
    console.log(document.getElementById('password').value)
    if (validateInputs()) {
 
      setLoading(true);
      const url = 'http://localhost:5000/login-signup';
      try{
        const response = await fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
           body:JSON.stringify({'email': document.getElementById('email').value, 'password': document.getElementById('password').value, 'name': document.getElementById('name').value})
    
          });
          console.log(response)
          if(response.ok){
            const result = await response.json();
            setLoading(false);
            if(result["success"] === true){
                setAlert({"type":"success","message":"Signup Successful"});
                navigate('/');  // Only navigate if inputs are valid
            }
            else{
                setAlert({"type":"error","message":"Signup Failed"});
                console.log('Signup failed')
          }
        }
      }
      catch (error){
        setAlert({"type":"error","message":"Server Error : Please contact the administrator"});
        console.log(error)
    }
    }};
  

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
      <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
      </Box>
      <Typography
        component="h1"
        variant="h4"
        sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.15rem)' }}
      >
        Sign Up
      </Typography>
      <Box
        component="form"
        onSubmit={handleSubmit}
        noValidate
        sx={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 2 }}
      >
        <FormControl>
            <FormLabel htmlFor="name">Name</FormLabel>
            <TextField
                id="name"
                type="name"
                name="name"
                placeholder="Your Name"
                autoFocus
                required
                fullWidth
                variant="outlined"/>
        </FormControl>

        <FormControl>
          <FormLabel htmlFor="email">Email</FormLabel>
          <TextField
            error={emailError}
            helperText={emailErrorMessage}
            id="email"
            type="email"
            name="email"
            placeholder="your@email.com"
            autoComplete="email"
            autoFocus
            required
            fullWidth
            variant="outlined"
            color={emailError ? 'error' : 'primary'}
          />
        </FormControl>
        <FormControl>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <FormLabel htmlFor="password">Password</FormLabel>
            <Link
              component="button"
              type="button"
              onClick={handleClickOpen}
              variant="body2"
              sx={{ alignSelf: 'baseline' }}
            >
              Forgot your password?
            </Link>
          </Box>
          <TextField
            error={passwordError}
            helperText={passwordErrorMessage}
            name="password"
            placeholder="••••••"
            type="password"
            id="password"
            autoComplete="current-password"
            autoFocus
            required
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
          {loading ? 'Signing up...' : 'Sign up'}
        </Button>
      </Box>
      {alert && <Alert severity={alert.type}>{alert.message}</Alert>}
    </Card>
  );
}