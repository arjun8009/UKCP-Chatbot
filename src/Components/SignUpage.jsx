import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Stack from '@mui/material/Stack';
import SignUpCard from './SignUpForm';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';

export default function SignUpPage(props) {
  return (
    <Stack
      direction="column"
      sx={{
        alignItems: 'center',
        justifyContent: 'center',
        height: 'min(100vh, 90%)', // Ensure the content is vertically centered
        p: { xs: 2, sm: 4 },
        gap: 4, // Space between logo and sign-in card
      }}
    >
      {/* Logo */}
      <stack direction="row">
        <img
            src="https://th.bing.com/th/id/OIP.hyEHEn1JS9ewOosdS1NzoQAAAA?w=300&h=250&rs=1&pid=ImgDetMain"
            alt="Logo"
            style={{ width: "200px", height: "200px" }}
        />
            <img
                src="https://th.bing.com/th/id/R.02660d7f125f6d135739a097ff33d69c?rik=jiQr3grpo4YkhA&pid=ImgRaw&r=0"
                alt="Logo"
                style={{ width: "200px", height: "200px" }}
            />
        </stack>

      {/* Sign-in Card */}
      <SignUpCard />
      <Typography fontSize={'10px'} sx={{ textAlign: 'center' }}>
          The content produced by the chatbot is AI-generated and may not always be accurate. Whilst we strive for accuracy, we encourage users to verify important information. The Met Office does not endorse the chatbot’s output. Met Office intellectual property is protected by Crown copyright <Link variant="body2" 
          href = "https://eur03.safelinks.protection.outlook.com/?url=https%3A%2F%2Fwww.nationalarchives.gov.uk%2Fdoc%2Fopen-government-licence%2Fversion%2F3%2F&data=05%7C02%7Cab1574%40exeter.ac.uk%7Ca9348b6628b74365e38c08ddb232d74f%7C912a5d77fb984eeeaf321334d8f04a53%7C0%7C0%7C638862653628897149%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=QHfi4076phprowYr3GBT4gGmPbywCC4wNgg2gfMNdQU%3D&reserved=0" 
          sx={{ alignSelf: 'center' }}> (OGL) </Link>.
          The UKCP18 chatbot is part of a research study. This study collects chatbot interaction to better understand user experiences, with access restricted to Arjun Biswas (a.biswas@exeter.ac.uk) and a collaborator from the University of Bath (Dr. Sachini Weerawardhana). 
          Identifiable data is securely stored on encrypted platform (Digital Ocean) and will be anonymised 10 days after submitting the follow-up survey, 
          after which individual data cannot be withdrawn. Anonymised data may be shared with the wider research team, and all data will be permanently deleted on 28 Feb 2035. 
          Participants can withdraw consent at any time before anonymisation, and all data handling complies with UK General Data Protection Regulation (GDPR).
        </Typography>
    </Stack>
  );
}