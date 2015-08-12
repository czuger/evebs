module ApplicationHelper

  def is_cedric_zuger
    user = current_user
    user.key_user_id == '3808229'
  end

end
