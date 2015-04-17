Rails.application.routes.draw do

  resources :price_advices, only: [:show]
  resources :choose_trade_hubs, only: [:edit, :update]

  resources :choose_items, only: [:new, :edit, :create, :update] do
    get :autocomplete_eve_item_name_lowcase, :on => :collection
  end

  root 'choose_items#edit'

end
