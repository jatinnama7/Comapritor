import { Route, Routes } from 'react-router-dom';
import Button from './Components/Button';

import Login from './Components/Login';
import Page1 from './pages/Page1';
import Home from './pages/Home';
import Navbar from './pages/Navbar';
import Page2 from './pages/Page2';
import Search from './pages/Search';


function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/navbar" element={<Navbar />} />
      <Route path="/button" element={<Button />} />
      <Route path="/login" element={<Login />} />
      <Route path="/page1" element={<Page1 />} />
      <Route path="/page2" element={<Page2 />} />
      <Route path="/search" element={<Search/>}/>

    </Routes>
  );
}

export default App;
