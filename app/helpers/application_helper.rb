module ApplicationHelper

  def is_cedric_zuger
    user = current_user
    user.key_user_id == '3808229'
  end

  def active_link( path = root_path )
    'active' if current_page?( path )
  end

end
