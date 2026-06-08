<template>
  <div class="admin-users" :class="{ light: !isDark }">
    <el-card class="filter-card" shadow="never">
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名..."
          clearable
          style="width: 200px;"
          @clear="loadUsers"
          @keyup.enter.native="loadUsers"
        >
          <i slot="prefix" class="el-icon-search"></i>
        </el-input>
        <el-select v-model="filterRole" placeholder="筛选角色" clearable style="width: 120px;" @change="loadUsers">
          <el-option label="全部" value=""></el-option>
          <el-option label="管理员" value="admin"></el-option>
          <el-option label="普通用户" value="user"></el-option>
        </el-select>
        <el-button icon="el-icon-refresh" @click="loadUsers">刷新</el-button>
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="username" label="用户名"></el-table-column>
        <el-table-column prop="role" label="角色">
          <template v-slot="{ row }">
            <el-tag :type="row?.role === 'admin' ? 'danger' : 'success'">
              {{ row?.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tenant_id" label="租户ID"></el-table-column>
        <el-table-column prop="conversation_count" label="对话数"></el-table-column>
        <el-table-column label="操作" width="120">
          <template v-slot="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleRoleChange(row)"
              :disabled="row?.id === currentUserId"
            >
              {{ row?.role === 'admin' ? '降级' : '升级' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :current-page="pagination.page"
          :page-size="pagination.page_size"
          :total="pagination.total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog title="切换角色" v-model:visible="roleDialogVisible" width="30%">
      <p>确定将用户 <span style="color: #5436da; font-weight: bold;">{{ selectedUser?.username }}</span> 
        {{ selectedUser?.role === 'admin' ? '降级为普通用户' : '升级为管理员' }} 吗？</p>
      <div slot="footer" class="dialog-footer">
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRoleChange">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { admin } from '@/api';
import { showSuccess, showError } from '@/utils';

export default {
  name: 'AdminUsers',

  data() {
    return {
      loading: false,
      searchKeyword: '',
      filterRole: '',
      tableData: [],
      pagination: {
        page: 1,
        page_size: 20,
        total: 0
      },
      roleDialogVisible: false,
      selectedUser: null
    };
  },

  computed: {
    isDark() {
      return this.$store.getters.isDark;
    },
    currentUserId() {
      return this.$store.getters.currentUser.id;
    }
  },

  mounted() {
    this.loadUsers();
  },

  methods: {
    async loadUsers() {
      this.loading = true;
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.page_size
        };
        if (this.filterRole) {
          params.role = this.filterRole;
        }
        if (this.searchKeyword) {
          params.keyword = this.searchKeyword;
        }
        const res = await admin.getUsers(params);
        // 过滤无效数据项，避免渲染错误
        const items = res?.data?.items || [];
        const validItems = items.filter(item => item !== undefined && item !== null && typeof item === 'object');
        this.tableData = [...validItems];
        this.pagination.total = res?.data?.total || 0;
      } catch (error) {
        showError('加载用户列表失败');
      } finally {
        this.loading = false;
      }
    },

    handlePageChange(page) {
      this.pagination.page = page;
      this.loadUsers();
    },

    handleRoleChange(row) {
      this.selectedUser = row;
      this.roleDialogVisible = true;
    },

    async confirmRoleChange() {
      if (!this.selectedUser) return;
      try {
        const newRole = this.selectedUser.role === 'admin' ? 'user' : 'admin';
        await admin.updateUserRole(this.selectedUser.id, newRole);
        showSuccess('角色切换成功');
        this.selectedUser.role = newRole;
        this.roleDialogVisible = false;
      } catch (error) {
        showError('角色切换失败');
      }
    },
  }
};
</script>

<style>
.admin-users {
  padding: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.table-card {
  border-radius: 8px;
}
.light .table-card { background: #fff; }

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.light :deep(.el-table) {
  background: #fff;
}
.light :deep(.el-table th) {
  background: #f5f7fa;
}
.light :deep(.el-table tr:hover > td) {
  background: #f0f0f0 !important;
}
.light :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #fafafa;
}
</style>