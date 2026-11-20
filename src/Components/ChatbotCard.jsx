import React from "react";
import ChatUI from "./ChatUI";
import {
  Box,
  Card,
  CardHeader,
  TextField,
  Button,
  Typography,
  Link,
  Avatar,
  Grid,
  Paper,
  Select
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import FeedbackTableWindow from "./FeedbackTableWindow"

export default function ChatbotCard() {

  const [open,setOpen] = React.useState(false)
  const [data,setData] = React.useState([])


  const handleClose = () =>{
    setOpen(false)
  }

  const handleOpen = async() => {
    try {
      const url = "http://localhost:5000/receive-feedback_db";
      const response = await fetch(url,{
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const result = await response.json();
        setData(result)
        
      } else {
          console.log("error")
      }
    } catch (error) {
      console.error('Error sending user input:', error);
    }
    setOpen(true)
  }


  return (
    <Card sx={{
        fontSize: { xs: "20px", sm: "28px", md: "34px" }, // scales by device
      }}>
      {open && <FeedbackTableWindow data={data} open={open} onClose ={handleClose}/>}
      <CardHeader
        title={<h2>UKCP18 ChatBot </h2>}
        sx={{
          background: "linear-gradient(rgb(0, 197, 148) 0%, rgb(0, 118, 88) 100%)",
          color: "white",
          display:"flex",
          flexDirection: { xs: "column", sm: "row" }, // column on phones, row on larger screens
          alignItems: { xs: "flex-start", sm: "center" },
          fontSize:"50px"
        }}
        avatar={[<img src= 'https://th.bing.com/th/id/OIP.hyEHEn1JS9ewOosdS1NzoQAAAA?w=300&h=250&rs=1&pid=ImgDetMain' style={{ width: "70px", height: "50px" }} />,
                <img src="https://th.bing.com/th/id/R.02660d7f125f6d135739a097ff33d69c?rik=jiQr3grpo4YkhA&pid=ImgRaw&r=0" style={{ width: "50px", height: "50px", marginLeft: "10px" }} />]}

        action={
          <Box
            sx={{
              display: "flex",
              flexWrap: "wrap", // allows wrapping
              gap: 1,
              justifyContent: { xs: "center", sm: "flex-end" },
            }}
          >
          <Button
            variant="outlined"
            endIcon={<SendIcon />}
            sx={{ color: "white", fontSize: { xs: "10px", sm: "12px", md: "14px" } }}
            component="a"
            target="_blank"
            rel="noopener noreferrer"
            href="https://uniofbath.questionpro.eu/ukcp-followup-mini"
          >
            Follow up Survey 
          </Button>
          
          <Button
            variant="outlined"
            endIcon={<SendIcon />}
            sx={{ color: "white", fontSize: { xs: "10px", sm: "12px", md: "14px" } }}
            component="a"
            target="_blank"
            rel="noopener noreferrer"
            href=" https://uniofbath.questionpro.eu/ukcp-followup-extended"
          >
            Follow up Survey Extended
          </Button>



          <Button
            variant="outlined"
            endIcon={<SendIcon />}
            sx={{ color: "white", fontSize: { xs: "10px", sm: "12px", md: "14px" } }}
            component="a"
            target="_blank"
            rel="noopener noreferrer"
            href="/ProposedTasksforUKCP18UserTesting.pdf"
          >
            View Tasks
          </Button>
        
        </Box>
       
        }
      />
      <Box sx={{ flex: 1, overflow: "auto" }}>
      <ChatUI />
      </Box>
      <Typography fontSize={'12px'} sx={{ textAlign: 'center' }}>
          The content produced by the chatbot is AI-generated and may not always be accurate. Whilst we strive for accuracy, we encourage users to verify important information. The Met Office does not endorse the chatbot’s output.
        </Typography>
    </Card>
  );
}
