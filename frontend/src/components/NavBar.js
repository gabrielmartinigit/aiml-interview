import { AppBar, Toolbar, Typography, Box, Button } from "@mui/material";
import logo from "../assets/logo.png";
import { useAuth } from "../hooks/useAuth";

export const NavBar = () => {
  const { user, logout } = useAuth();

  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <Box sx={{ mr: 2 }}>
          <img src={logo} alt="AWS logo" width={60} />
        </Box>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Simulador de Entrevistas
        </Typography>
        {!!user && (
          <>
            <Typography>{user["userEmail"]}</Typography>
            <Button color="highlight" onClick={logout}>
              logout
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;
