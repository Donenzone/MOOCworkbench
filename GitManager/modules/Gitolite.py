from MOOCworkbench.settings import BASE_DIR
from git import Repo

class GitoliteRepo():
    def __init__(self, repo_name, username):
        self.repo_name = repo_name
        self.users = {}
        if username:
            self.users[username] = 'RW+'

    def add_user(self, username, rights):
        self.users[username] = rights

    def remove_user(self, username):
        del self.users[username]

    def __repr__(self):
        return self.pretty_print()

    def extract_rights(self, rights):
        right_str = ''
        if 'READ' in rights:
            right_str += 'R'
        if 'WRITE' in rights:
            right_str += 'W'
        if 'RW' in rights:
            right_str += 'RW+'
        return right_str

    def list_files_in_repo(self):
        # check if this user repository exists
        file_list = []
        for obj in self.repo.tree():
            file_list.append({'file': obj.name, 'hash': obj, 'isdir': path.isdir('{0}/{1}'.format(self.PATH, obj.name))})
        return file_list

    def list_git_commits(self):
        commit_list = []
        for commit in self.repo.iter_commits():
            commit_list.append({'date': commit.authored_date, 'author': commit.author, 'hash': commit.hexsha, 'message': commit.message})
        return commit_list

    def view_file_in_repo(self, file_name):
        tree = self.repo.tree()
        blob = tree / file_name
        data = blob.data_stream.read()
        return data

    def list_files_in_repo_folder(self, folder_name):
        tree = self.repo.tree()
        folder = tree / folder_name
        file_list = []
        for obj in folder:
            file_list.append({'file': obj.name, 'hash': obj, 'isdir': path.isdir('{0}/{1}'.format(self.PATH, obj.name))})
        return file_list

    def pretty_print(self):
        config_file = "repo {0}\n".format(self.repo_name)
        for key, value in self.users.items():
            config_file += "\t{0} \t= \t{1}\n".format(self.extract_rights(value), key)
        config_file += "\tR \t= \t@workers"
        return config_file

class Gitolite():
    def __init__(self):
        self.repos = []
        self.user_groups = []
        self.read_config_file()

    def add_repo(self, repo_name, username):
        repo = GitoliteRepo(repo_name, username)
        self.repos.append(repo)
        self.write_config_file()
        return repo

    def add_user_to_repo(self, repo_name, username, rights):
        repo = self.find_repo(repo_name)
        repo.add_user(username, rights)
        return True

    def add_user_group_to_repo(self, repo_name, group_name, rights):
        repo = self.find_repo(repo_name)
        repo.add_user("@{0}".format(group_name), rights)
        return True

    def remove_user_from_repo(self, repo_name, username):
        repo = self.find_repo(repo_name)
        repo.remove_user(username)
        return True

    def find_repo(self, repo_name):
        repo = next((x for x in self.repos if x.repo_name == repo_name), None)
        if repo is not None:
            return repo
        return Exception("Repository not found")

    def add_ssh_key(self, username, ssh_public_key):
        new_key_file = open("{0}.pub".format(username), 'w+')
        new_key_file.write(ssh_public_key)
        new_key_file.close()

    def read_config_file(self):
        with open("{0}/gitrepositories/gitolite-admin/conf/gitolite.conf".format(BASE_DIR)) as f:
            config = f.readlines()

        active_repo = ''
        for line in config:
            line = line.replace('\n', '')
            line = line.strip()
            if line.startswith('repo'):
                repo = line.split(' ')
                del repo[0]
                active_repo = repo[0]
                self.add_repo(active_repo, None)
            elif line.startswith('R'):
                user = line.split('=')
                self.add_user_to_repo(active_repo, user[1].strip(), user[0].strip())
            elif line.startswith('@'):
                print("Group")

    def write_config_file(self):
        updated_config = open("{0}/gitrepositories/gitolite-admin/conf/gitolite.conf".format(BASE_DIR), 'w+')

        for repo in self.repos:
            updated_config.write('{0}\n\n'.format(repo.pretty_print()))
        updated_config.close()

    def push_config_changes(self):
        print("Activate new changes")
        admin_repo = Repo("{0}/gitrepositories/gitolite-admin/".format(BASE_DIR))
        admin_repo.index.add(['conf/gitolite.conf',])
        admin_repo.index.commit("Added new repository")
        admin_repo.remote().push()

git = Gitolite()
git.add_repo('new_test', 'jochem')
git.push_config_changes()
