import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Slider from '@mui/material/Slider';
import { Alert, Button } from '@mui/material';
import {Grid} from '@mui/material';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Checkbox from '@mui/material/Checkbox';
import ListItemText from '@mui/material/ListItemText';

const DynamicDropdownForm = ({ data, messageinfo, addtomessages }) => {
  const [formData, setFormData] = useState({});
  const [questionstate, setQuestionstate] = useState([]);
  const [disable,setDisable] = useState([])
  const [disablesubmit,setDisableSubmit] = useState(true)
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tempValues, setTempValues] = useState({}); // For temporary input values
  
  useEffect(() => {
  console.log("Data received in DataForm:", data);
  if (data && typeof data === 'string'){
    setDisableSubmit(false)
  }
  
  if (data && Object.keys(data).length > 0) {
    const questions = Object.entries(data)
      .sort(([keyA], [keyB]) => {
        const order = ['start_year', 'end_year'];
        const indexA = order.indexOf(keyA);
        const indexB = order.indexOf(keyB);
        
        // If both keys are in the order array, sort by their position
        if (indexA !== -1 && indexB !== -1) {
          return indexA - indexB;
        }
        // If only keyA is in the order array, it comes first
        if (indexA !== -1) return -1;
        // If only keyB is in the order array, it comes first
        if (indexB !== -1) return 1;
        // If neither is in the order array, maintain original order
        return 0;
      })
      .map(([question, config]) => ({
        question,
        ...config
      }));
    setQuestionstate(questions);
  }
}, [data]);

  const handlesubmit = async () => {
    try{

      const url = "http://localhost:5000/Submit-data-request"
      setLoading(true)
      const res = await fetch(url,{
        method : 'POST',
        headers:{
        'Content-Type': 'application/json'
        },
        body:JSON.stringify({email:sessionStorage.getItem("email"),time:new Date()})
      });
      if (res.ok) {

        console.log("Submit success")
        setDisableSubmit(true)
        const messages = await res.json()
        addtomessages(messages)

      }
    }catch(err){
      console.log("ERR in submit")
    }finally{
      setLoading(false)
    }
  }


  const sendDataToBackend = React.useCallback(async (updatedData) => {
  try {
    const fulldata = {email:sessionStorage.getItem("email"), data:updatedData}
    const url = "http://localhost:5000/data-parameter"
    
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(fulldata)
    });

    if (!res.ok) {
      console.error('Failed to send data:', res.statusText);
      return; // Exit if the request failed
    }

    // 1. Get the response body as text first
    const responseText = await res.text();
    let responseData;

    // 2. Try to parse the text as JSON
    try {
      responseData = JSON.parse(responseText);
    } catch (e) {
      // 3. If parsing fails, it's just plain text
      responseData = responseText;
      console.log("Received plain text response:", responseData);
      setDisableSubmit(false);
      return;
    }finally {
    setLoading(false); // stop loading when done
    }

    if(Object.hasOwn(responseData[0], "llm_extraction")){
        addtomessages(responseData)
      }
    else{
      // 4. Process the valid JSON response
      // Assuming the structure is an array, e.g., [{ content: ... }]
      const entries = responseData[0].content;

      setDisable(prev => [...prev, ...questionstate.map(q => q.question)]);

      if (typeof entries === 'string') {
        // Handles cases like "success" inside the JSON
        console.log("Final response:", entries);
        setDisableSubmit(false);
      } else {
        // Handles a JSON object with more questions
        const questions = Object.entries(entries)
        .sort(([keyA], [keyB]) => {
          const order = ['start_year', 'end_year'];
          const indexA = order.indexOf(keyA);
          const indexB = order.indexOf(keyB);
          
          // If both keys are in the order array, sort by their position
          if (indexA !== -1 && indexB !== -1) {
            return indexA - indexB;
          }
          // If only keyA is in the order array, it comes first
          if (indexA !== -1) return -1;
          // If only keyB is in the order array, it comes first
          if (indexB !== -1) return 1;
          // If neither is in the order array, maintain original order
          return 0;
        }).map(([question, config]) => ({
          question,
          ...config
        }));
        const mergedData = [...questionstate, ...questions];
        setQuestionstate(mergedData);
      }
    }
    

  } catch (err) {
    console.error('Error sending data:', err);
  }
}, [questionstate]);

  const debounce = (func, wait) => {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        func(...args);
      }, wait);
    };
  };

  const debouncedSendDataToBackend = React.useMemo(
  () =>
    debounce((data) => {
      setLoading(true);
      sendDataToBackend(data).finally(() => setLoading(false));
    }, 2000),
  [sendDataToBackend]
  );

  const handleChange = (question, value,immediate) => {
    const updated = { ...formData, [question]: value };
    setFormData(updated);
    if ("start_year" in updated && "end_year" in updated) {
      const start = Number(updated.start_year);
      const end = Number(updated.end_year);
      if (isNaN(start) || isNaN(end)) {
      setError("Start year and End year must be numbers");
      setDisableSubmit(true);
      return;
      }

      if (start > end) {
        setError("Start year cannot be greater than End year");
        setDisableSubmit(true);
        return;
      }
      setError("");
    }

    const allAnswered = questionstate.every(q => updated[q.question] !== undefined && updated[q.question] !== '');
    if (allAnswered) {
      if (immediate){
        setLoading(true);
        sendDataToBackend(updated).finally(()=>setLoading(false));
      }
      else{
        debouncedSendDataToBackend(updated);
      }
    }
  };

  return (
  
  <Box
    className="min-h-[200px] p-6 max-w-md mx-auto space-y-4"
    style={{ minWidth: "300px", maxWidth: "100%" }}
    sx={{ position: "relative", overflow: "visible" }}
  >
        {error && (
      <Alert severity="error" onClose={() => setError("")}>
        {error}
      </Alert>  
    )}
    {loading && (
      <Box
        sx={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          bgcolor: 'rgba(0,0,0,0.7)',
          color: 'white',
          px: 4,
          py: 2,
          borderRadius: 2,
          zIndex: 9999,
          pointerEvents: "none",
        }}
      >
        Loading...
      </Box>
    )}
    {/* Title */}
    <Typography variant="h5" gutterBottom>
      UKCP Data Functionality
    </Typography>

    <Typography variant='body1'>
      {messageinfo}
    </Typography>

    {/* Use Stack to add vertical spacing between entries */}
    <Stack spacing={3}>
      {questionstate.map(({ question, type, options }) => {
        const [rawmin, rawmax] = options || [0, 100];
        const min = Number(rawmin);
        const max = Number(rawmax);

        return (
          <Grid
            container
            key={question}
            spacing={2}
            alignItems="center"
          >
            {/* Label */}
            <Grid item xs={4}>
              <Typography variant="body1">{question}</Typography>
            </Grid>

            {/* Input */}
            <Grid item xs={8}>
              {type === "text" && (
                <TextField
                  fullWidth
                  disabled={disable.includes(question)}
                  variant="outlined"
                  value={formData[question] || ""}
                  onChange={(e) => handleChange(question, e.target.value, false)}
                />
              )}

              {type === "range" && (
                <TextField
                  type="number"
                  fullWidth
                  value={tempValues[question] ?? formData[question] ?? ""}
                  disabled={disable.includes(question)}
                  onChange={(e) => {
                    const rawValue = e.target.value; // keep as string
                    setTempValues((prev) => ({ ...prev, [question]: rawValue }));
                    const num = Number(rawValue);
                    let errorMessage = "";
                    if (isNaN(num) || num < min) {
                      errorMessage = `Value cannot be less than ${min}`;
                      setError(errorMessage); 
                    } else if (num > max) {
                      
                      errorMessage = `Value cannot be greater than ${max}`;
                      setError(errorMessage); 
                    }
                    else{
                      handleChange(question, num, false); // Immediate final update
                    }
                  }}
                  inputProps={{
                    min: min,
                    max: max,
                    step: 1,
                  }}
                  variant="outlined"
                  size="small"
                />
              )}

              { type === "multiselect" && (

                <Select
                  fullWidth
                  multiple
                  value={formData[question] || []}
                  onChange={(e) => handleChange(question, e.target.value, false)}
                  disabled={disable.includes(question)}
                  renderValue={(selected) => selected.join(", ")} // Display selected values as comma-separated
                >
                  {(options || []).map((option, idx) => (
                    <MenuItem key={idx} value={option}>
                      <Checkbox checked={(formData[question] || []).includes(option)} />
                      <ListItemText primary={option} />
                    </MenuItem>
                  ))}
                </Select>
              )}

              {type === "select" && (
                <Select
                  fullWidth
                  value={formData[question] || ""}
                  onChange={(e) => handleChange(question, e.target.value, false)}
                  disabled={disable.includes(question)}
                >
                  <MenuItem value="" disabled>
                    Choose an Option
                  </MenuItem>
                  {(options || []).map((option, idx) => (
                    <MenuItem key={idx} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              )}
            </Grid>
          </Grid>
        );
      })}
    </Stack>

    {/* Submit Button */}
      <Button
        variant="contained"
        color="primary"
        disabled={disablesubmit}
        onClick={() => handlesubmit()}
      >
        Submit
      </Button>

  </Box>
);}


export default DynamicDropdownForm;
