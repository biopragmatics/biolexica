"""Review OBO Foundry new ontology requests."""

import requests

ISSUES_URL = "https://api.github.com/repos/OBOFoundry/OBOFoundry.github.io/issues"


def get_issues():
    """Retrieve all new ontology request issues."""
    issues = requests.get(ISSUES_URL, params={"labels": "new ontology"}).json()
    results = []
    for issue in issues:
        issue_id = issue["number"]
        user = issue["user"]["login"]
        body = issue["body"]

        lines = iter(body.splitlines())
        download_link = None
        for line in lines:
            # print(line)
            if "Ontology Download Link" in line:
                while not (download_link := next(lines)):
                    pass
                break

        results.append((issue_id, user, download_link))
    return results


def main():
    get_issues()


if __name__ == "__main__":
    main()
