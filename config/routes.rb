Rails.application.routes.draw do

  get 'sale_records/index'

  resource :sale_records, only: [:index ] do
    get :items_sums
    get :station_sums
    get :stations_items_sums
  end

  resources :identities

  resource :user, only: [:edit,:update] do
    get :help
  end

  namespace :price_advices do
    get :advice_prices
    get :show_challenged_prices
  end


  resource :choose_trade_hubs, only: [:edit, :update]

  resource :choose_items, only: [:new, :edit, :create, :update] do
    get :autocomplete_eve_item_name_lowcase, :on => :collection
  end

  resource :sessions, only: [:new] do
    get :screenshots
  end
  match 'auth/:provider/callback', to: 'sessions#create', via: [:get, :post]
  match 'auth/failure', to: 'sessions#failure', via: [:get, :post]
  # match 'auth/failure', to: redirect('/'), via: [:get, :post]
  match 'signout', to: 'sessions#destroy', as: 'signout', via: [:get, :post]

  root 'price_advices#advice_prices'

end
