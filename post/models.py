from django.db import models
from account.models import MyUser

def post_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'uploads/posts/post_{0}/{1}'.format(instance.user.id, filename)

class Post(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=post_directory_path)
    video = models.FileField(upload_to=post_directory_path)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name

class PostLikes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='post_liked')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.post, self.user)



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='post_comments')
    text = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.post.id, self.user.name)