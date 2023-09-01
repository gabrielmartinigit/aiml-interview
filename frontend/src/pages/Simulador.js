import Recorder from "../components/Recorder";
import RecordsTable from "../components/RecordsTable";
import { Box, Container } from "@mui/material";

function Simulador() {
  return (
    <Container
      disableGutters
      maxWidth="md"
      component="main"
      sx={{ pt: 8, pb: 6 }}
    >
      <Box display="flex" justifyContent="center" alignItems="center">
        <Recorder />
      </Box>
      <Box mt={2}>
        <RecordsTable />
      </Box>
    </Container>
  );
}

export default Simulador;
