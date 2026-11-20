import React, { useState, useEffect } from 'react';
import { 
  Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, CircularProgress 
} from '@mui/material';
import Papa from 'papaparse';

const SimpleCSVTable = ({ csvUrl }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!csvUrl) return;

    setLoading(true);
    Papa.parse(csvUrl, {
      download: true,
      header: true, // Converts rows into objects using the first row as keys
      skipEmptyLines: true,
      complete: (results) => {
        setData(results.data);
        setLoading(false);
      },
      error: (error) => {
        console.error("Error parsing CSV:", error);
        setLoading(false);
      }
    });
  }, [csvUrl]);

  if (loading) return <CircularProgress />;
  if (data.length === 0) return <div>No data found.</div>;

  // Get headers from the first object keys
  const columns = Object.keys(data[0]);

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            {columns.map((col) => (
              <TableCell key={col} sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5' }}>
                {col}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, index) => (
            <TableRow key={index} hover>
              {columns.map((col) => (
                <TableCell key={`${index}-${col}`}>
                  {row[col]}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default SimpleCSVTable;