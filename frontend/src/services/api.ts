import axios from 'axios';
import {
  User,
  DiscoveryField,
  PolicyItem,
  BatchRun,
  ProtectedCustomer,
  AuditEvent,
  DashboardStats
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'https://flyyy-ai-production.up.railway.app';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor: attach token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');

  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Authentication
export const authService = {
  login: async (username: string, password: string) => {
    const cleanUsername = username.trim();

    const res = await api.post(
      '/auth/login',
      {
        username: cleanUsername,
        password: password,
      }
    );

    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await api.get('/auth/me');
    return res.data;
  }
};

// Dashboard
export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const res = await api.get('/dashboard/stats');
    return res.data;
  },

  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  }
};

// Discovery
export const discoveryService = {
  discover: async (): Promise<{
    fields: DiscoveryField[];
    total_fields: number;
    discovered_at: string;
  }> => {
    const res = await api.post('/discover');
    return res.data;
  }
};

// Policies
export const policyService = {
  getPolicies: async (): Promise<{
    policies: PolicyItem[];
    active_version: number;
  }> => {
    const res = await api.get('/policies');
    return res.data;
  },

  updatePolicies: async (policies: PolicyItem[]) => {
    const res = await api.put('/policies', { policies });
    return res.data;
  }
};

// Source
export const sourceService = {
  getConfig: async () => {
    const res = await api.get('/sources/config');
    return res.data;
  },

  uploadCSV: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await api.post('/sources/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    return res.data;
  },

  getRecords: async (page = 1, pageSize = 20) => {
    const res = await api.get(
      `/sources/records?page=${page}&page_size=${pageSize}`
    );

    return res.data;
  }
};

// Batch
export const batchService = {
  runBatch: async (
    source = 'DATABASE',
    batchSize = 1000
  ): Promise<BatchRun> => {
    const res = await api.post('/batch/run', {
      source,
      batch_size: batchSize
    });

    return res.data;
  },

  getBatches: async (): Promise<BatchRun[]> => {
    const res = await api.get('/batch');
    return res.data;
  },

  getBatch: async (id: string): Promise<BatchRun> => {
    const res = await api.get(`/batch/${id}`);
    return res.data;
  }
};

// Customers
export const customerService = {
  getCustomers: async (
    page = 1,
    pageSize = 20,
    search = ''
  ): Promise<{
    items: ProtectedCustomer[];
    total: number;
  }> => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize)
    });

    if (search) {
      params.append('search', search);
    }

    const res = await api.get(`/customers?${params.toString()}`);

    return res.data;
  },

  getCustomer: async (id: string): Promise<ProtectedCustomer> => {
    const res = await api.get(`/customers/${id}`);
    return res.data;
  },

  exportCSV: async () => {
    const res = await api.get('/export/protected', {
      responseType: 'blob'
    });

    const url = window.URL.createObjectURL(
      new Blob([res.data])
    );

    const link = document.createElement('a');

    link.href = url;
    link.setAttribute(
      'download',
      'protected_customers.csv'
    );

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.URL.revokeObjectURL(url);
  }
};

// Marketing
export const marketingService = {
  sendEmail: async (
    recipient: string,
    campaignId: string,
    templateId: string
  ) => {
    const res = await api.post('/actions/send-email', {
      recipient,
      campaign_id: campaignId,
      template_id: templateId
    });

    return res.data;
  }
};

// Bounce
export const bounceService = {
  simulateBounce: async (
    email: string,
    event = 'BOUNCE',
    reason = 'MAILBOX_NOT_FOUND'
  ) => {
    const res = await api.post('/webhooks/email', {
      email,
      event,
      reason
    });

    return res.data;
  }
};

// Controlled Reveal
export const revealService = {
  reveal: async (
    subjectId: string,
    field: string,
    purpose: string,
    reference: string
  ) => {
    const res = await api.post('/reveal', {
      subject_id: subjectId,
      field,
      purpose,
      reference
    });

    return res.data;
  }
};

// Audit
export const auditService = {
  getEvents: async (
    page = 1,
    pageSize = 20,
    actor = '',
    action = '',
    purpose = '',
    result = ''
  ): Promise<{
    items: AuditEvent[];
    total: number;
  }> => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize)
    });

    if (actor) {
      params.append('actor', actor);
    }

    if (action) {
      params.append('action', action);
    }

    if (purpose) {
      params.append('purpose', purpose);
    }

    if (result) {
      params.append('result', result);
    }

    const res = await api.get(`/audit?${params.toString()}`);

    return res.data;
  }
};