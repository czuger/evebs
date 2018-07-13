Rails.application.routes.draw do

  resource :admin_tools, only: [ :show ] do
    get :denied
    get :activity
    get :min_prices_timings
    get :min_prices_timings_overview
    get :items_users
    get :crest_price_history_update
  end

  resources :characters, only: [ :edit, :update ] do
    get :share_list, controller: :production_lists
    post :share_list_validate, controller: :production_lists
    get :accept_shared_list, controller: :production_lists
    get :accept_shared_list_validate, controller: :production_lists
  end

  resources :components_to_buy, only: [ :show ]

  resources :items, only: [ :show ] do
    get :cost
    get :trade_hub_detail
  end

  resources :components, only: [ :index, :show ] do
    get :trade_hub_detail
  end

  resource :list_items, only: [ :edit, :update ] do
    get :my_items_list
  end

  resources :production_lists, only: [ :edit, :update ] do
  end

  # resources :jita_margins, only: [ :index, :update ]

  # resources :identities

  resource :users, only: [:edit, :update] do
    get :edit_password
    post :change_password
  end

  namespace :price_advices do
    get :advice_prices
    get :advice_prices_monthly
    get :show_challenged_prices
    get :empty_places
    post :update_basket
  end

  resource :choose_trade_hubs, only: [:edit, :update]

  resource :choose_items, only: [ :edit ] do
    get :items_tree
    get :select_all_items
    post :select_items
  end

  resource :sessions, only: [:new] do
  end

  match 'auth/:provider/callback', to: 'sessions#create', via: [:get, :post]
  match 'auth/failure', to: 'sessions#failure', via: [:get, :post]
  # match 'auth/failure', to: redirect('/'), via: [:get, :post]
  match 'signout', to: 'sessions#destroy', as: 'signout', via: [:get, :post]

  root 'jita_margins#index'

end
