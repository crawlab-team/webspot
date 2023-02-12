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
  setup(props) {
    const url = ref('');
    const results = ref('');
    const html = ref('');
    const error = ref('');

    const htmlString = computed(() => {
      return atob(props.html);
    });

    const onUrlChange = (value) => {
      url.value = value;
    };

    const onSubmit = async () => {
      const res = await axios.post(`/detect`, {url: url.value});
      results.value = res.data.results;
      html.value = res.data.html;
      error.value = res.data.error;
    };

    onBeforeMount(async () => {
      const urlParam = new URL(window.location.href).searchParams.get('url');
      if (urlParam) {
        url.value = urlParam;
        await onSubmit();
      }
    });

    const formattedError = computed(() => {
      if (!props.error) return '';
      return props.error.split('\n').join('<br>');
    });

    return {
      url,
      results,
      html,
      error,
      htmlString,
      onUrlChange,
      onSubmit,
      formattedError,
    };
  },
  template: `
<top-navbar :url="url" @url-change="onUrlChange" @submit="onSubmit"/>
<div class="main-container">
  <template v-if="url">
    <!--error-->
    <template v-if="error">
      <el-result icon="error" style="width: 100%" title="An error occurred" sub-title="Please try again">
        <template #extra>
          <pre v-html="formattedError" style="text-align: left; color: var(--color-red); border: 1px solid var(--color-light-grey); padding: 10px; background: #ffffff"/>
        </template>
      </el-result>
    </template>
    <!--./error-->

    <!--results-->
    <template v-else-if="results && html">
      <nav-sidebar :results="results" @submit="onSubmit" @change="onUrlChange"/>
      <preview-container :html="html"/>
    </template>
    <!--./results-->
  </template>

  <!--no-url-->
  <template v-else>
    <el-empty style="width: 100%" description="Please enter the URL to start" style="padding-bottom: 15%">
      <div class="url-wrapper" style="display: flex; width: 640px;">
        <el-input v-model="url" placeholder="Please enter the URL" @keyup.enter="onSubmit"/>
        <el-button type="primary" @click="onSubmit" style="margin-left: 5px">Submit</el-button>
      </div>
    </el-empty>
  </template>
  <!--./no-url-->
</div>
`
};
