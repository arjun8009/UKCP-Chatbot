import React, { useEffect, useState, UseRef } from "react";
import Axios from "axios";
import {
  useTheme,
  useMediaQuery,
  Box,
  TextField,
  Button,
  Typography,
  Avatar,
  Drawer,
  Grid,
  Paper,
  InputAdornment,
  CircularProgress,
  Fab,
  Menu,
  Tooltip
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ReactMarkdown from 'react-markdown';
import DescriptionIcon from '@mui/icons-material/Description';
import ClosableWindow from "./ClosableWindow";
import IconButton from '@mui/material/IconButton';
import remarkGfm from 'remark-gfm';
import BotIcon from '@mui/icons-material/Android';
import UserIcon from '@mui/icons-material/Person';
import Person from "@mui/icons-material/Person";
import ThreeDotsAnimation from "./threedots";
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import MenuIcon from '@mui/icons-material/Menu'
import FeedbackModal from "./FeedbackModal";
import MenuItem from '@mui/material/MenuItem';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import Switch from '@mui/material/Switch';
import DataAnalysis from './DataAnalysis'
import { Construction } from "@mui/icons-material";
import styled from "@emotion/styled";
import { useNavigate,useLocation } from "react-router-dom";
import DynamicDropdownForm from "./DataForm";
import '../markdown-styles.css'

export default function ChatUI() {
  const [input, setInput] = React.useState("");
  const [isButtonDisabled, setButtonDisabled] = useState(true);
  const [isButtonDisabledsources, setButtonDisabledsources] = useState(true);
  const buttonref = React.useRef(null)
  const [image,setImage] = React.useState([{'image':false,'url':" ",'caption':" "}])
  const [messages, setMessages] = React.useState([
    { role: "assistant" ,content: "Hi there! I am UKCP18 ChatBot. I can answer questions related to UKCP18.<br><strong> Max Latency or Response Time : </strong> <br> Answer from Reports : 50s <br> Data Analysis : 1m 30s <br><strong> Data Unavailability : </strong> <br> 1. Hourly data at all resolutions and Daily data at 2.2 km Resolution"},]);
  const [sources,setSources] = React.useState([])
  const [isLoading, setIsLoading] = useState(false);

  const [open, setOpen] = useState(false);
  const [feedbackopen,setFeedbackopen] = useState(false);
  const [feedbackdata,setFeedbackdata] = useState('')
  const [dataukcp,setDataukcp] = useState(false)
  const [pipelinechoice,setPipelineChoice] = useState('4')
  const [sessionStart,setSessionStart] = useState(false)
  const messagesEndRef = React.useRef(null);
  const imagesEndRef = React.useRef(null);
  const navigate = useNavigate();
  const location = useLocation();
  const hasChecked = React.useRef(false);
  const [extraction,setExtraction] = React.useState(false)
  

  const LargeTooltip = styled(Tooltip)({
    popper: {
      '& .MuiTooltip-tooltip': {
        fontSize: "1.5rem", // Adjust font size for bigger tooltip text
        padding: "12px", // Increase padding for a larger appearance
      },
    },
  });
  
  

  useEffect(() => {

    if (hasChecked.current) return
    hasChecked.current = true
    
    const navigated = sessionStorage.getItem('navigateToUI');
    
    console.log("session storage navigated",navigated,location.pathname)
    if (location.pathname === '/UI' && !navigated) {
      navigate('/');
    }else{
      sessionStorage.removeItem('navigateToUI')
    }
  }, [location.pathname, navigate]);

  useEffect(() => {


    const startTime = new Date();
    setSessionStart(startTime);
    sessionStorage.setItem('startTime', startTime);

    const handleUnload = () => {
      const endTime = new Date();
      const formatDate = (date) =>
        date.toLocaleString('en-GB', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false, // Use 24-hour format
        }).replace(',', '');

      const formattedStart = formatDate(startTime);
      const formattedEnd = formatDate(endTime);
      const email = sessionStorage.getItem('email');
      const data = JSON.stringify({ "start":formattedStart, "end":formattedEnd, "email": email , "userAgent": navigator.userAgent , "platform": navigator.platform});
      console.log("Handle Unload function")
      navigator.sendBeacon('http://localhost:5000/api/session-end', data);
      //console.log('Session duration:', duration);
      // Send the duration to the backend
    };
    window.addEventListener('beforeunload', handleUnload);

    return () => {
      window.removeEventListener('beforeunload', handleUnload);
    };
  },[]);
  

  const handleOpen = (index) => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handlefeedbackopen = (message) => {
    setFeedbackopen(true)

    const feedbackdata = {"question":messages[messages.length - 2].content,"answer":message.content,"extracts":sources.sources}
    setFeedbackdata(feedbackdata)
  }


  const handlefeedbackclose = () => {
    setFeedbackopen(false)
  }

  const UpdateMessages = (message) => {

    const message_inc = message[0]
    if(Object.hasOwn(message_inc,"llm_extraction")){
      setExtraction(message_inc.llm_extraction)
    }
    const message_sources = message[1]
    setMessages([...messages,message_inc])
    if(message_sources.sources.length===1 & message_sources.sources[0].hasData === true){
      setDataukcp(true)
    }else{
      setDataukcp(false)
    }

    if (message_sources.sources[0].hasImage === true){
      setImage([...image,{'image':false,'url':" ",'caption':" "},{'image':true,'url':message_sources.sources[0].Url,'caption':message_sources.sources[0].captions}])
    }
    else{
      setImage([...image,{'image':false,'url':" ",'caption':" "},{'image':false,'url':" ",'caption':" "}])
    }

    if (sources.length === 0) {
        setSources([message_sources]);
    } else {
        setSources([...sources,message_sources]);
      }
      setButtonDisabled(true)

  }

  const handleSend = async() => {
    

    var newMessage = {role: "user",content: input, hasData:dataukcp, pipelineIndex: pipelinechoice, dataOption : "/Both", time: new Date() , email: sessionStorage.getItem('email')};
    
    
    if(sources.length >=1 && sources[sources.length-1].sources[sources[sources.length-1].sources.length-1].incomplete === true){
       newMessage = {role: "user",content: input, hasData:dataukcp,incomplete:true,pipelineIndex: pipelinechoice, dataOption : "/Both",time: new Date() , email: sessionStorage.getItem('email')};
    }

    const updated_message = [...messages, newMessage]
    console.log(updated_message)
    setMessages(updated_message);
    
    setInput("");
    setIsLoading(true);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000);
    try {
      const queryParams = `?updated_message=${encodeURIComponent(updated_message)}`;
      console.log("llm_extraction",extraction)
      
      let url = "http://localhost:5000/receive-data"
      if (extraction===true){
        
        url = "http://localhost:5000/llm-decide"

      }
    
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
       body:JSON.stringify({'updated_message':updated_message}),
       signal: controller.signal,



      });
      clearTimeout(timeoutId);
      if (response.ok) {
        // set there is no image for user message
        const result = await response.json();
        console.log("Assistant message",result[0])
        if (result[0] && Object.hasOwn(result[0], 'llm_extraction')) {
        console.log("Setting extraction to:", result[0].llm_extraction);
        setExtraction(result[0].llm_extraction);
      }
        if(result[0].Form === true){
            
            setMessages([...updated_message, result[0]]);
            setSources([...sources,result[1]]);
        }
        else{
          setMessages([...updated_message, result[0]]);
          
          if(result[1].sources.length===1 & result[1].sources[0].hasData === true){
            setDataukcp(true)
          }else{
            setDataukcp(false)
          }
          if (result[1].sources[0].hasImage === true){
            //setImage([...image,{'image':false,'url':" "}])
            setImage([...image,{'image':false,'url':" ",'caption':" "},{'image':true,'url':result[1].sources[0].Url,'caption':result[1].sources[0].captions}])
          }
          else{
            setImage([...image,{'image':false,'url':" ",'caption':" "},{'image':false,'url':" ",'caption':" "}])
          }
          if (sources.length === 0) {
            
            setSources([result[1]]);
          } else {
            setSources([...sources,result[1]]);
          }
          setButtonDisabled(true)
        } }else {
          // Handle errors
        }
    } catch (error) {
      console.error('Error sending user input:', error);
      const errorMessage = {role: "assistant",content: "Sorry this request is too large for this chatbot to handle."};
      setMessages([...updated_message, errorMessage]);
    } finally{
      setIsLoading(false);
    }
  };

  const AppendData = (message) =>{
    
    const newMessage = {
      role: "assistant",
      content: message, 
    };
    setMessages((prevMessages) => [...prevMessages, newMessage]);

  }

  const fetchDataAndAppend = async () => {
    try {
      const url = "http://localhost:5000/list-files"
      setIsLoading(true)
      const response = await fetch(url,{
        method:"POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body:JSON.stringify({'email':sessionStorage.getItem("email")})
        
      })
      const result = await response.json();

      
      const newMessage = {
        role: "assistant",
        content: result.message, 
      };

      // Append the new message to the messages state
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    } catch (error) {
      console.error("Error fetching data:", error);
      const errorMessage = {
        role: "assistant",
        content: "Error fetching data for data-analysis. Please try again later.",
      };

      // Append error message in case of failure
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    }
    finally{
      setIsLoading(false)
    }
  };

  useEffect(() => {
    // This useEffect will run whenever sources state is updated
    
    // Perform additional actions here
  }, [sources]);

  useEffect(() => {
  console.log("Extraction state successfully changed to:", extraction);
  // You can trigger logic here that depends on the NEW state
}, [extraction]); // This runs whenever extraction changes

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
    if (imagesEndRef.current) {
      imagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages,image,isLoading]); // Scroll when messages or loading state changes
  
  

  useEffect(() => {
    // This useEffect will run whenever sources state is updated
    // Perform additional actions here
  }, [image]);
  

  const handleInputChange = (event) => {
    setInput(event.target.value);
    const text = event.target.value
    if(text.length > 0){
      setButtonDisabled(false)
    }else{
      setButtonDisabled(true)
    }
  };

  const [draweropen, setDrawerOpen] = useState(false);

  const handledrawerOpen = ()=>{
    setDrawerOpen(true)
  }

  const handleDrawerClose = ()=>{
    setDrawerOpen(false)
  }

  const handleChangeselect = (event) => {
    setPipelineChoice(event.target.value)
  }

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [mobiledrawerOpen, setMobileDrawerOpen] = useState(false);

  const handelkeypress = (event) => {
    if(event.key=='Enter'){
      buttonref.current.click();
    }
  };
  
  return (

    <Box
      sx={{
        height: "85vh",
        display: "flex",
        flexDirection: image.some((img) => img.image === true) ? { xs: "column", md: "row" } : "column",
        bgcolor: "grey.200",
        overflow: "hidden",
      }}
    >

  
    <Box
      sx={{
          flex: image.some((img) => img.image === true) ? { xs: 1, md: 0.6 } : 1,
          minHeight: 0,
          display: "flex",
          flexDirection: "column",
          bgcolor: "grey.200",
        }}
    >
      

      <Box sx={{
            flex: 1,              
            overflowY: "auto",
            p: 2,
            minHeight: 0,          
            position: "relative",
          }}>
        

    {
      messages.map((message,index) => (
      <React.Fragment key={index}>
      <Message message={message} image={image[index]} updater = {UpdateMessages} />

      {message.role === 'assistant' && index!==0 && (
        <Box sx={{position:'relative',marginRight:'60px',top:'-50px'}}>
          <IconButton onClick={() => handlefeedbackopen(message)}>
            <ThumbDownIcon/>
          </IconButton>
          <IconButton onClick={() => handleOpen(index)}><DescriptionIcon/>
        </IconButton>
        </Box>
      
      )}
      {open && ((index/2)-1)>=0 && (index%2==0) && (<ClosableWindow data = {sources} messages={messages} open={open} onClose={handleClose} />)}

    </React.Fragment>

    ))}

    {isLoading && (
        <Message key="loading" message={{ content: <ThreeDotsAnimation />, role: "assistant" }} />
      )}
      {<div ref={messagesEndRef}/>}
      {<FeedbackModal data={feedbackdata} open={feedbackopen} onClose={handlefeedbackclose} />}
    </Box>

    <Box  sx={{
      p: 2,
      backgroundColor: "background.default",
      position: "sticky",
      bottom: 0,
      width: "100%",
      display: "flex",
      justifyContent: "space-between",
    }}>
     <Grid container spacing={2} alignItems="center">
      <Grid item xs={12}>
        <TextField
          size="small"
          fullWidth
          placeholder="Type a message"
          variant="outlined"
          value={input}
          onKeyDown={handelkeypress}
          onChange={handleInputChange}
          InputProps={{
            endAdornment: (

              <>
              <IconButton onClick={handleSend} disabled = {isButtonDisabled} ref = {buttonref} edge="end">
                <SendIcon />
              </IconButton>

              {image.some((img) => img.image === true) && isMobile && (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setDrawerOpen(true)}>
                      <MenuIcon />
                    </IconButton>
                  </InputAdornment>
                )}

              </>
            ),
          }}
        />
      </Grid>
    </Grid>
    </Box>
    </Box>

    {image.some((img) => img.image === true) && !isMobile && (
    <Box
      sx={{
        flex: 0.4,
        borderLeft: "1px solid #ccc",
        height: "100%",
        overflowY: "auto",
        textAlign: "center",
        bgcolor: "white",
      }}
    >
    <DataAnalysis open={true} close={handleDrawerClose} images={image} scrollRef={imagesEndRef} />  
    </Box>)}

     {image.some((img) => img.image === true) && isMobile && (
        <Drawer
          anchor="right"
          open={draweropen}
          onClose={() => setDrawerOpen(false)}
          PaperProps={{ sx: { width: "80%" } }}
        >
          <DataAnalysis open={true} close={() => setDrawerOpen(false)} images={image} scrollRef={imagesEndRef} />
        </Drawer>
      )}
    
    </Box>
  );}


const Message = ({ message, image, updater }) => {
  const isBot = message.role === "assistant";
  const hasImage = image && image.image === true;
  const hasDatas = message.Data === true; // Assuming the parameter is named "Data"


  // Function to handle download
  const handleDownload = async () => {
    try {
      //'https://king-prawn-app-gl3kg.ondigitalocean.app/download-zip'

      const response = await fetch("https://king-prawn-app-gl3kg.ondigitalocean.app/download", {
        method: 'POST', // Or 'GET' depending on your API
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ emailid: sessionStorage.getItem('email') }), // Assuming you need to pass some identifier to the backend
      });

      // Assuming the backend sends the zip file as a binary response
      const zipData = await response.blob();

      // Create a temporary URL for the zip file
      const url = window.URL.createObjectURL(new Blob([zipData]));
      
      // Create a temporary link element and trigger the download
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'data.zip');
      document.body.appendChild(link);
      link.click();
      // Clean up
      URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading zip file:', error);
    }
  };



  const renderMessageContent = () => {
    console.log("Current Message", message)
    if (message.Form && message.content){
      return <DynamicDropdownForm data={message.content} messageinfo = {message.optional_message} addtomessages = {updater} />; 
    }


    const isHTML = (text) => /<\/?[a-z][\s\S]*>/i.test(text);
    if (typeof(message.content) == "string") {
      return (
      /* REMOVE Typography here - use a div or Box with the class */
      <div className="markdown-container">
        {isHTML(message.content) ? (
          <div dangerouslySetInnerHTML={{ __html: message.content }} />
        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        )}
      </div>
    );
    } else {
      return (
        <Typography 
          variant="body2" 
          component="span" // Changes from <p> to <span> to prevent block stretching
          sx={{ 
            fontSize: "0.95rem", 
            lineHeight: 1.5,
            display: "inline-block", // Allows the width to be determined by content
            textAlign: "left"
          }}
        >
          {message.content}
        </Typography>
    );
    }
  };

  return (
    <Box
       sx={{
      display: "flex",
      justifyContent: isBot ? "flex-start" : "flex-end",
      mb: 1.5,
      maxWidth: "100%",
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: isBot ? "row" : "row-reverse",
          alignItems: "flex-start",
          maxWidth: "55%",
          gap: 1,
        }}
      >
        <Avatar 
        sx={{ 
          bgcolor: isBot ? "#4f8ef7" : "#9c27b0",
          width: 32, 
          height: 32 
        }}
      >
        {isBot ? <BotIcon fontSize="small" /> : <Person fontSize="small" />}
      </Avatar>


        {isBot ? (<Paper
            elevation={1}
              sx={{
                p: 2,
                backgroundColor: isBot ? "#f5f5f5" : "#4f8ef7",
                color: isBot ? "black" : "white",
                borderRadius: isBot 
                  ? "20px 20px 20px 5px" 
                  : "20px 20px 5px 20px",
                whiteSpace: "pre-wrap",
                width: "fit-content",
                whiteSpace:"normal",
                boxShadow: 1,
              }}
            >
            {renderMessageContent()}
            {hasDatas && (
              <Button
                variant="contained"
                color="primary"
                sx={{ marginTop: '8px' }}
                onClick={handleDownload} // Call handleDownload function on button click
              >
                Download Data
              </Button>
            )}
            </Paper>) : (
            
            <Paper
            elevation={1}
            sx={{
              p: 2,
              backgroundColor: isBot ? "#f5f5f5" : "#4A90E2",
              color: isBot ? "black" : "white",
              borderRadius: isBot 
                ? "20px 20px 20px 5px" 
                : "20px 20px 5px 20px",
              whiteSpace:"normal",
              width: "fit-content",
              boxShadow: 1,
            }}
            >
             {renderMessageContent()} 
            
          </Paper>
        )}
        
        </Box>
      </Box>
  );
};
