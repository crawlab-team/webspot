const {ref, computed, watch, onBeforeMount} = Vue;
const {ElMessage} = ElementPlus;
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
    const isLoading = ref(false);

    const htmlString = computed(() => {
      return atob(props.html);
    });

    const onUrlChange = (value) => {
      url.value = value;
    };

    const onSubmit = async () => {
      try {
        isLoading.value = true;
        const res = await axios.post(`/detect`, {url: url.value});
        if (res) isLoading.value = false;
        results.value = res.data.results;
        html.value = res.data.html;
        error.value = res.data.error;
      } catch (error) {
        isLoading.value = false;
        const {detail} = error?.response?.data;
        ElMessage({message: detail, type: 'warning', offset: 80});
      }
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

    watch(() => url.value, (val) => {
      // if the input url changes, the page data should be cleared.
      if (val) {
        results.value = '';
        html.value = '';
        error.value = '';
        isLoading.value = false;
      }
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
      isLoading,
    };
  },
  template: `
<top-navbar :url="url" @url-change="onUrlChange" @submit="onSubmit" :is-loading="isLoading"/>
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

    <!--skeleton-->
    <template v-else-if="isLoading">
      <el-skeleton style="padding-top: 2%;" animated :throttle="500">
        <template #template>
          <div style="display: flex;">
            <el-skeleton style="width: 240px; margin-left: 2%;" :rows="25" />
            <el-skeleton style="flex: 1; margin: 0 10%;" :rows="25" />
          </div>
        </template>
      </el-skeleton>
    </template>
    <!--./skeleton-->

    <!--results-->
    <template v-else-if="results && html">
      <nav-sidebar :results="results" @submit="onSubmit" @change="onUrlChange"/>
      <preview-container :html="html"/>
    </template>
    <!--./results-->

    <!--empty-->
    <template v-else>
      <el-empty style="width: 100%; padding-bottom: 15%;" description="Please enter the URL to start">
        <div class="url-wrapper" style="display: flex; width: 640px;">
          <el-input v-model="url" placeholder="Please enter the URL" @keyup.enter="onSubmit"/>
          <el-button type="primary" @click="onSubmit" style="margin-left: 5px" :loading="isLoading">Submit</el-button>
        </div>
      </el-empty>
    </template>
    <!--./empty-->
  </template>

  <!--no-url-->
  <template v-else>
    <el-empty style="width: 100%; padding-bottom: 15%;" description="Please enter the URL to start">
      <div class="url-wrapper" style="display: flex; width: 640px;">
        <el-input v-model="url" placeholder="Please enter the URL" @keyup.enter="onSubmit"/>
        <el-button type="primary" @click="onSubmit" style="margin-left: 5px" :loading="isLoading">Submit</el-button>
      </div>
    </el-empty>
  </template>
  <!--./no-url-->
</div>
`
};
