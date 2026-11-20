import * as React from "react";
import { styled } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import IconButton from "@mui/material/IconButton";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import CardContent from "@mui/material/CardContent";
import SimpleCSVTable from "./DataTable";

const HeaderBox = styled("div")(({ theme }) => ({
  display: "flex",
  justifyContent: "flex-end",
  padding: theme.spacing(1),
}));

export default function DataAnalysis({ open, close, images, scrollRef }) {
  // Filter images where image.image is true
  const imagesfil = images.filter((image) => image.image === true);

  return (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        overflowY: "auto",
        bgcolor: "grey.100",
        textAlign:"center"
      }}
    >
      {/* Header with Close Icon */}
      <HeaderBox>
        <Typography variant="heading2" textAlign="center">Graphs and Images</Typography>
      </HeaderBox>

      {/* Render Images and Captions */}
      <Box
        sx={{
          padding: 1,
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        {imagesfil && imagesfil.length > 0 ? (
  imagesfil.map((item, index) => {
    // Force url to be an array if it's just a string
    const urlArray = Array.isArray(item.url) ? item.url : [item.url];
    
    return urlArray.map((imgUrl, i) => (
      <Card key={`${index}-${i}`} sx={{ width: "100%", mb: 2 }}>
        {(() => {
          if (!imgUrl) return null; // Handle empty URLs

          const isCSV = imgUrl.toLowerCase().endsWith('.csv');
          const isHTML = imgUrl.toLowerCase().endsWith('.html');

          if (isCSV) return <SimpleCSVTable csvUrl={imgUrl} />;
          
          if (isHTML) return (
            <Box sx={{ height: 500, width: "100%", bgcolor: "#f5f5f5" }}>
              <iframe
                title={`Plot ${index}-${i}`}
                src={imgUrl}
                style={{ width: '100%', height: '100%', border: 'none' }}
              />
            </Box>
          );

          return (
            <CardMedia
              component="img"
              height="500"
              image={imgUrl}
              sx={{ objectFit: "contain", bgcolor: "#000" }}
            />
          );
        })()}
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            {/* Safe check for caption array */}
            {(item.caption && item.caption[i]) || "No caption provided."}
          </Typography>
        </CardContent>
      </Card>
    ));
  })
) : (
  <Typography>No images to display.</Typography>
)}
        <div ref={scrollRef}/>
      </Box>
    </Box>
  );
}
