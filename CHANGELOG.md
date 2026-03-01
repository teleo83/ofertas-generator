# 📦 Ofertas Generator - Histórico de Versões

---

## 🚀 v1.1.1 - Pagamento Funcionando (Webhook Real)

### ✅ Implementado
- Integração completa com Mercado Pago
- Checkout Sandbox funcional
- Webhook validando pagamento aprovado
- Atualização automática do plano do usuário
- Suporte a múltiplos planos (free, premium, vitalicio)
- Correção estrutural do campo `plan`
- Dashboard Admin sincronizado com banco
- Cloudflare Tunnel funcionando para testes externos

### 🔒 Segurança
- Plano só atualiza se status = approved
- Uso de external_reference para identificar usuário

---

## 🚀 v1.1 - Sistema FREE com limite diário

### ✅ Implementado
- Contador de 3 envios diários no plano FREE
- Reset automático a cada 24h
- Exibição visual no dashboard
- Bloqueio automático após atingir limite

---

## 🚀 v1.0 - Base do Sistema

### ✅ Implementado
- Autenticação (login / cadastro)
- Dashboard do usuário
- Integração API Shopee
- Publicação automática no Telegram
- Painel Admin