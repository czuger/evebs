module Modules::SharedPlList

  def set_user_to_show( user )
    @shared_production_list = user.user_pl_share != nil
    @shared_production_list ? user.user_pl_share : user
  end
end