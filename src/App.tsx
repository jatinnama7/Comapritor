import { Route, Routes } from 'react-router-dom';
import Button from './pages/Button';

import Home from './pages/Home';
import Login from './pages/Login';
import Navbar from './pages/Navbar';
import Page1 from './pages/Page1';
import Page2 from './pages/Page2';
import Search from './pages/Search';
import Loading from './pages/loading';
import Product from './pages/Product';
import Compared from './pages/Compared';
import Productlist from './pages/Productlist';
import Explorepage from './pages/Explorepage';
import Contacts from './pages/Contacts';
import Reels from './pages/Reels';
import Dashboard from './pages/Dashboard';
import ThreeD from './pages/ThreeD';


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
      <Route path="/loading"element={<Loading/>}/>
      <Route path="/product"element={<Product/>}/>
      <Route path="/compared"element={<Compared/>}/>
      <Route path="/list"element={<Productlist/>}/>
      <Route path="/explore"element={<Explorepage/>}/>
      <Route path="/contacts"element={<Contacts/>}/>
      <Route path="/reels"element={<Reels/>}/>
      <Route path="/dashboard" element={<Dashboard/>}/>
      <Route path="/threeD" element={<ThreeD/>}/>

    </Routes>
  );
}

export default App;
