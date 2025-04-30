import "./App.css";

import { Menu } from "./components/Shared/Menu";
import { AppRouter } from "./Router/AppRouter";

function App() {
  return (
    <>
      <Menu />
      <AppRouter />
    </>
  );
}

export default App;
