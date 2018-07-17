module Modules::SharedPlList

  def set_user_to_show( user )
    @shared_production_list = user.current_character.character_pl_share
    @shared_production_list ? @shared_production_list.user : user
  end
end