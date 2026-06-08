/**
 * @file API统一导出
 * @description 统一导出所有API模块，方便使用
 * @author aichat_upend
 */

import * as auth from './auth';
import * as conversation from './conversation';
import { chat } from './chat';
import * as admin from './admin';

export {
  auth,
  conversation,
  chat,
  admin
};
