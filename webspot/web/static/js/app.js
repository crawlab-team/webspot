const {ref, computed, watch, onBeforeMount} = Vue;
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
      internalUrl.value = value;
    };
    watch(() => props.url, () => internalUrl.value = props.url);
    onBeforeMount(() => {
      const url = new URL(window.location.href);
      internalUrl.value = url.searchParams.get('url');
    });
    const onSubmit = () => {
      // replace query string "url" with the value of internalUrl
      const url = new URL(window.location.href);
      url.searchParams.set('url', internalUrl.value);

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
    <!--error-->
    <template v-if="error">
      <el-empty style="width: 100%" :description="'Error occurred: ' + error" style="padding-bottom: 15%">
    </template>
    <!--./error-->

    <!--results-->
    <template v-else>
      <nav-sidebar :results="results" @submit="onSubmit" @change="onUrlChange"/>
      <preview-container :html="html"/>
    </template>
    <!--./results-->
  </template>

  <!--no-url-->
  <template v-else>
    <el-empty style="width: 100%" description="Please enter the URL to start" style="padding-bottom: 15%">
      <div class="url-wrapper" style="display: flex; width: 640px;">
        <el-input v-model="internalUrl" placeholder="Please enter the URL" @keyup.enter="onSubmit"/>
        <el-button type="primary" @click="onSubmit" style="margin-left: 5px">Submit</el-button>
      </div>
    </el-empty>
  </template>
  <!--./no-url-->
</div>
`
};
