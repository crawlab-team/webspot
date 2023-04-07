const {h} = Vue;
const {createStore} = Vuex;
const {ElNotification} = ElementPlus;

const defaultRequestForm = {
  method: 'request',
  no_async: false,
};

const store = createStore({
  state() {
    return {
      requests: [],
      activeRequestId: undefined,
      requestForm: undefined,
      activeResult: undefined,
      activeResultTabName: 'overview',
      activeResultDialogVisible: false,
      previewMode: undefined,
    };
  },
  getters: {
    isEmpty(state) {
      return state.requests.length === 0;
    },
    activeRequest(state) {
      return state.requests.find((request) => request.id === state.activeRequestId);
    },
    activeRequestStatus(state, getters) {
      return getters.activeRequest ? getters.activeRequest.status : '';
    },
    activeRequestResults(state, getters) {
      return getters.activeRequest ? getters.activeRequest.results : [];
    },
    activeRequestFormattedError(state, getters) {
      if (!getters.activeRequest) return '';
      if (!getters.activeRequest.error) return '';
      return getters.activeRequest.error.split('\n').join('<br>');
    },
    requestForm(state) {
      if (state.requestForm) {
        return {...state.requestForm};
      }
      if (localStorage.getItem('requestForm')) {
        try {
          return JSON.parse(localStorage.getItem('requestForm'));
        } catch {
        }
      }
      localStorage.setItem('requestForm', JSON.stringify(defaultRequestForm));
      state.requestForm = {...defaultRequestForm};
      return {...defaultRequestForm};
    },
    activeResultDetector(state) {
      return state.activeResult ? state.activeResult.detector : '';
    },
    activeResultName(state) {
      return state.activeResult ? state.activeResult.name : '';
    },
    previewMode(state) {
      if (state.previewMode) {
        return state.previewMode;
      }
      state.previewMode = localStorage.getItem('previewMode') || 'highlight';
      return state.previewMode;
    },
  },
  mutations: {
    setRequests(state, requests) {
      state.requests = requests;
    },
    setActiveRequestId(state, id) {
      state.activeRequestId = id;
    },
    setRequestForm(state, requestForm) {
      state.requestForm = {
        ...requestForm,
      };
      localStorage.setItem('requestForm', JSON.stringify({
        ...requestForm,
      }));
    },
    resetRequestForm(state) {
      localStorage.setItem('requestForm', JSON.stringify(defaultRequestForm));
      return {...defaultRequestForm};
    },
    setActiveResult(state, result) {
      state.activeResult = result;
    },
    resetActiveResult(state) {
      state.activeResult = undefined;
    },
    setActiveResultTabName(state, tabName) {
      state.activeResultTabName = tabName;
    },
    resetActiveResultTabName(state) {
      state.activeResultTabName = 'overview';
    },
    setActiveResultDialogVisible(state, visible) {
      state.activeResultDialogVisible = visible;
    },
    setPreviewMode(state, mode) {
      state.previewMode = mode;
      localStorage.setItem('previewMode', mode);
    },
  },
  actions: {
    async getRequests({commit, state}) {
      const res = await axios.get(`/api/requests`);
      if (JSON.stringify(res.data) === JSON.stringify(state.requests)) {
        return;
      }
      commit('setRequests', res.data);

      // Set active request id if it's not set yet
      if (state.activeRequestId === undefined && res.data.length > 0) {
        commit('setActiveRequestId', res.data[0].id);
      }
    },
    async postRequest({getters, commit, dispatch}, request) {
      const res = await axios.post(`/api/requests`, {
        ...getters.requestForm,
        ...request,
      });
      await dispatch('getRequests');
      await ElNotification({
        title: 'Triggered request',
        message: h('span', [
          h('label', {}, ['URL: ']),
          h('a', {href: `${request.url}`, target: '_blank'}, [request.url]),
        ]),
        type: 'info',
      });

      // Set result id as active
      commit('setActiveRequestId', res.data.id);
    },
    async getRequestNode({commit, state}) {
    },
  }
});

export default store;
