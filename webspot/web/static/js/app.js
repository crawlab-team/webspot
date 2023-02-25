const {ref, computed, onBeforeMount} = Vue;
const {useStore} = Vuex;
import RequestHistory from './components/request-history.js';
import TopNavbar from './components/top-navbar.js';
import NavSidebar from './components/nav-sidebar.js';
import PreviewContainer from './components/preview-container.js';

export default {
  components: {
    RequestHistory,
    TopNavbar,
    NavSidebar,
    PreviewContainer,
  },
  setup() {
    const store = useStore();

    onBeforeMount(() => {
      store.dispatch(`getRequests`);
    });

    const isEmpty = computed(() => store.getters['isEmpty']);

    const activeRequestStatus = computed(() => store.getters['activeRequestStatus']);

    const activeRequestFormattedError = computed(() => store.getters['activeRequestFormattedError']);

    const requestForm = ref({
      url: '',
    });

    const isLoading = ref(false);
    const onSubmit = async () => {
      isLoading.value = true;
      await store.dispatch('postRequest', {...requestForm.value});
      isLoading.value = false;
    };

    return {
      isEmpty,
      activeRequestStatus,
      activeRequestFormattedError,
      requestForm,
      isLoading,
      onSubmit,
    };
  },
  template: `
<top-navbar/>

<div class="main-container">
  <request-history/>

  <!--is-empty-->
  <template v-if="isEmpty">
    <el-empty style="width: 100%; padding-bottom: 15%;" description="Please enter the URL to start">
      <div class="url-wrapper" style="display: flex; width: 640px;">
        <el-input v-model="requestForm.url" placeholder="Please enter the URL" @keyup.enter="onSubmit"/>
        <el-button type="primary" @click="onSubmit" style="margin-left: 5px" :loading="isLoading">Submit</el-button>
      </div>
    </el-empty>
  </template>
  <!--./is-empty-->

  <template v-else>
    <!--error-->
    <template v-if="activeRequestStatus === 'error'">
      <el-result class="error-message-container" icon="error" style="" title="An error occurred" sub-title="Please try again">
        <template #extra>
          <pre class="error-message" v-html="activeRequestFormattedError"/>
        </template>
      </el-result>
    </template>
    <!--./error-->

    <!--skeleton-->
    <template v-else-if="activeRequestStatus === 'pending'">
      <el-skeleton style="padding-top: 2%; flex: 1" animated :throttle="500">
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
    <template v-else-if="activeRequestStatus === 'success'">
      <nav-sidebar/>
      <preview-container/>
    </template>
    <!--./results-->
  </template>
</div>
`
};
