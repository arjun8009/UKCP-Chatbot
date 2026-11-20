import React, { useState } from "react";
import { Button, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import FeedBackTable from "./FeedBackTable"

export default function FeedbackTableWindow({data, open, onClose }) {

  return (
    <div>
      <Dialog open={open} onClose={onClose} fullWidth>
        <DialogTitle>
          Feedback Dialog
          <Button
            variant="text"
            color="error"
            style={{ position: "absolute", right: "8px", top: "8px" }}
            onClick={onClose}
          >
            <CloseIcon />
          </Button>
        </DialogTitle>
        <DialogContent>
          <FeedBackTable rows={data}/>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
