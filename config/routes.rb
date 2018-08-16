Rails.application.routes.draw do

  resources :user_to_user_duplication_requests
  resource :admin_tools, only: [ :show ] do
    get :denied
    get :activity
    get :min_prices_timings
    get :min_prices_timings_overview
    get :items_users
    get :crest_price_history_update
  end

  resources :characters, only: [] do
    get :share_list, controller: :production_lists
    post :share_list_update, controller: :production_lists
    get :accept_shared_list, controller: :production_lists
    post :accept_shared_list_update, controller: :production_lists

    get :download_assets,  controller: :components_to_buy
    post :download_assets_start,  controller: :components_to_buy
  end

  resources :production_lists, only: [ :edit, :update, :create ]
  post :remove_production_list_check, controller: :production_lists
  get :update_shared_list, controller: :production_lists


  resources :user_sale_orders, only: [ :index ]
  get :send_my_orders, controller: :user_sale_orders, action: :send_my_orders_edit
  post :send_my_orders, controller: :user_sale_orders
  get :get_sent_orders, controller: :user_sale_orders
  get :get_sent_orders_result, controller: :user_sale_orders

  get :show_challenged_prices, controller: :user_sale_orders

  get :download_orders, controller: :user_sale_orders
  post :download_orders_start, controller: :user_sale_orders

  resource :blueprints, only: [:show]

  resources :components_to_buy, only: [ :show ]
  get :components_to_buy_show_raw,  controller: :components_to_buy

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

  resource :users, only: [:edit, :update]

  namespace :price_advices do
    get :advice_prices
    get :advice_prices_weekly
    get :empty_places
  end

  resource :choose_trade_hubs, only: [:edit, :update]

  resource :choose_items, only: [ :edit ] do
    get :items_tree
    get :select_all_items
    post :select_items
  end

  match 'auth/:provider/callback', to: 'sessions#create', via: [:get, :post]
  match 'auth/failure', to: 'sessions#failure', via: [:get, :post]
  # match 'auth/failure', to: redirect('/'), via: [:get, :post]
  match 'signout', to: 'sessions#destroy', as: 'signout', via: [:get, :post]

  root 'jita_margins#index'

end
