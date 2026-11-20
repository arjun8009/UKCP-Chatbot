import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Checkbox from '@mui/material/Checkbox';
import { Button } from '@mui/material';
import { v4 as uuidv4 } from 'uuid';
import FeedbackEditModal from './FeedBackEditModal';



export default function FeedBackTable({rows}) {

  const [Selected,setSelected] = React.useState(null)
  const [SelectedId,setSelectedId] = React.useState(null)
  const [rowCount,setRowCount] = React.useState(0)
  const [open,setOpen] = React.useState(false)
  const [tableData,setTableData] = React.useState(rows)
  
  const onSelectClick = (event,row)=>{
    console.log(row)
    const checked = event.target.checked
    if(checked){
      setSelectedId(row.index)
      setSelected(row)
      setRowCount(rowCount+1)
    }else{
      setSelectedId(null)
    }
  }

  const reloadData = async() => {
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
        setTableData(result)
        
      } else {
          console.log("error")
      }
    } catch (error) {
      console.error('Error sending user input:', error);
    }
  }

  const onHandleClick = () => {
    setOpen(true)
  }

  const handleClose = () =>{
    reloadData()
    setOpen(false)
  }

  React.useEffect(()=>{
    reloadData();
  },[]);
  
  return (
    <div>
      {open && <FeedbackEditModal data={Selected} open={open} onClose={handleClose}/>}
      <div>
        <Button color='primary' variant='contained' onClick={onHandleClick} sx={{marginBottom:"10px"}}>Edit</Button>
      </div>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell align='right'>Sel</TableCell>
              <TableCell align="right">Question</TableCell>
              <TableCell align="right">Answer</TableCell>
              <TableCell align="right">Feedback</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.map((row) => (
              <TableRow key={row.index} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}> 
                <TableCell padding="checkbox">
                  <Checkbox
                    color="primary"
                    checked={row.index===SelectedId}
                    onChange={(event)=>onSelectClick(event,row)}
                  />
                </TableCell>
                <TableCell align="right">{row.question}</TableCell>
                <TableCell align="right">{row.answer}</TableCell>
                <TableCell align="right">{row.feedback}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}