const {ref, computed, watch} = Vue;
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
  setup(props) {
    const htmlString = computed(() => {
      return atob(props.html);
    });
    const internalUrl = ref('');
    const onUrlChange = (value) => {
      console.debug(value);
      internalUrl.value = value;
    };
    watch(() => props.url, () => internalUrl.value = props.url);
    const onSubmit = () => {
      // replace query string "url" with the value of internalUrl
      const url = new URL(window.location.href);
      url.searchParams.set('url', internalUrl.value);
      console.debug(url.href);

      // navigate to the new url
      window.location.href = url.href;
    };
    return {
      htmlString,
      internalUrl,
      onUrlChange,
      onSubmit,
    };
  },
  template: `
<top-navbar :url="url" @url-change="onUrlChange" @submit="onSubmit"/>
<div class="main-container">
  <template v-if="url">
    <nav-sidebar :results="results" @submit="onSubmit" @change="onUrlChange"/>
    <preview-container :html="html"/>
  </template>
  <template v-else>
    <el-empty style="width: 100%" description="Please enter the URL to start" style="padding-bottom: 15%">
      <div class="url-wrapper" style="display: flex; width: 640px;">
        <el-input v-model="internalUrl" placeholder="Please enter the URL" @keyup.enter="onSubmit"/>
        <el-button type="primary" @click="onSubmit" style="margin-left: 5px">Submit</el-button>
      </div>
    </el-empty>
  </template>
</div>
`
};
