import React, { useState } from "react";
import { Button, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import {Typography,TextField,Divider,Alert} from "@mui/material";
import Snackbar from '@mui/material/Snackbar';

export default function FeedbackEditModal({data, open, onClose }) {

    const [input,setInput] = React.useState('')
    const [alert,setAlert] = React.useState(false)
    const [alertContent,setAlertContent] = React.useState('')

    const handleClose = ()=>{
        setAlert(false)
    }
    const handleInputChange = (event) => {

        setInput(event.target.value);
        const text = event.target.value
      };

    const handleSubmit = async() => {
        const feedback = {"question":data.question,"answer":data.answer,"extracts":data.extracts,"feedback":input,"index":data.index}
        try {
            const response = await fetch('http://localhost:5000/update-feedback_db', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ feedback }),
            });
            if (response.ok) {
              const result = await response.json();
              setAlert(true)
              setAlertContent("Data saved Successfully")
              setInput('')
              onClose()
            } else {
                setAlert(true)
                setAlertContent("Data saved Unsuccessfully")
                console.log("error")
            }
          } catch (error) {
            console.error('Error sending user input:', error);
        console.log("Submitted")
    }}

  return (
    <div>
        <Snackbar
        open={alert}
        autoHideDuration={3000}
        onClose={handleClose}
        message={alertContent}
      />
      <Dialog open={open} onClose={onClose} fullWidth style={{maxHeight:'120vh'}}>
        <DialogTitle>
          <Typography sx={{fontWeight:'bold'}}>Feedback</Typography>
          <Button
            variant="text"
            color="error"
            style={{ position: "absolute", right: "8px", top: "8px" }}
            onClick={onClose}
          >
            <CloseIcon />
          </Button>
        </DialogTitle>
        <Divider/>
        <DialogContent style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Typography sx={{ alignSelf: 'center', mb: 2 }}>Please Provide the Updated Feedback</Typography>
          <TextField defaultValue={data.feedback} onChange={handleInputChange} placeholder="Please provide feedback to improve the performance of the system" fullWidth ></TextField>

        </DialogContent>
        <DialogActions>
          <Button onClick={handleSubmit} color="primary">
            Submit
          </Button>
          <Button onClick={onClose} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
