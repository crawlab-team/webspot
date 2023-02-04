import TopNavbar from './components/top-navbar.js';
import NavSidebar from './components/nav-sidebar.js';
import PreviewContainer from './components/preview-container.js';

export default {
  components: {
    TopNavbar,
    NavSidebar,
    PreviewContainer,
  },
  props: {
    url: String,
    html: String,
    results: String,
  },
  template: `
<top-navbar :url="url"></top-navbar>
<div class="main-container">
  <nav-sidebar :results="results"/>
  <preview-container :html="html"/>
</div>
`
};
