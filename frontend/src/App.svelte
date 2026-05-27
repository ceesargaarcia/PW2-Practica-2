<script>
  import { authState } from './lib/auth.svelte.js';
  import Navbar         from './components/Navbar.svelte';
  import Toasts         from './components/Toasts.svelte';
  import LoginPage      from './pages/LoginPage.svelte';
  import RegisterPage   from './pages/RegisterPage.svelte';
  import ProductsPage   from './pages/ProductsPage.svelte';
  import ProfilePage    from './pages/ProfilePage.svelte';
  import AdminUsersPage from './pages/AdminUsersPage.svelte';

  // $state() — página actual (SPA sin router externo)
  let currentPage = $state(authState.token ? 'products' : 'login');

  // $derived() — si el usuario está autenticado
  const isAuthenticated = $derived(!!authState.token);

  // $effect() — redirige al login si el token desaparece
  $effect(() => {
    if (!authState.token && !['login','register'].includes(currentPage)) {
      currentPage = 'login';
    }
  });

  function navigate(page) { currentPage = page; }
</script>

{#if isAuthenticated}
  <Navbar {currentPage} {navigate} />
{/if}

<main>
  {#if currentPage === 'login'}
    <LoginPage {navigate} />
  {:else if currentPage === 'register'}
    <RegisterPage {navigate} />
  {:else if currentPage === 'products'}
    <ProductsPage {navigate} />
  {:else if currentPage === 'profile'}
    <ProfilePage {navigate} />
  {:else if currentPage === 'admin'}
    <AdminUsersPage {navigate} />
  {:else}
    <ProductsPage {navigate} />
  {/if}
</main>

<Toasts />

<style>
  :global(*) { box-sizing: border-box; margin: 0; padding: 0; }
  main { min-height: calc(100vh - 64px); }
</style>
