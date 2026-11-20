import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import SignInCard from './SignInCard';

export default function SignInSide(props) {
  return (
    <>
      <CssBaseline />
      <Grid container sx={{ height: '100vh' }}>
        {/* Left side with the image */}
        <Grid
          item
          xs={12}
          md={6}
          sx={{
            backgroundImage: 'url(https://www.metoffice.gov.uk/binaries/content/gallery/metofficegovuk/hero-images/weather/atmosphere/high-and-low-pressure.jpg)',
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        
        {/* Right side with the sign-in form */}
        <Grid
          item
          xs={12}
          md={6}
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: { xs: 4, md: 8 },
          }}
        >
          <Box sx={{ textAlign: 'center', marginBottom: 4 }}>
            {/* Logos (side by side) */}
            <img
              src="https://th.bing.com/th/id/OIP.hyEHEn1JS9ewOosdS1NzoQAAAA?w=300&h=250&rs=1&pid=ImgDetMain"
              alt="Logo 1"
              style={{ width: '100px', height: '100px', marginRight: '16px' }}
            />
            <img
              src="https://th.bing.com/th/id/R.02660d7f125f6d135739a097ff33d69c?rik=jiQr3grpo4YkhA&pid=ImgRaw&r=0"
              alt="Logo 2"
              style={{ width: '100px', height: '100px' }}
            />
          </Box>
          {/* Sign-in Card */}
          <SignInCard />
        </Grid>
      </Grid>
    </>
  );
}